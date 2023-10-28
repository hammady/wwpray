import os
import datetime
import logging
import json
import time
from copy import deepcopy
from boto3 import client as boto3_client
from botocore.exceptions import ClientError


# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def detect_changes(old_data, new_data, save_to_file=None):
    logger.debug(f"Old data: {old_data}")
    logger.debug(f"New data: {new_data}")

    # copy new_data so that we don't modify it
    new_data = deepcopy(new_data)

    # generate UTC timestamps in ISO format
    now = datetime.datetime.utcnow()
    ts = now.isoformat()
    today = now.date().isoformat()

    changes = {}

    # iterate through masjids in new data
    for new_key, new_value in new_data["masjids"].items():
        # check if masjid doesn't exist in old data
        old_value = old_data["masjids"].get(new_key)
        if old_value is None:
            # masjid doesn't exist in old data, add it to changes
            changes[new_key] = True
            new_value["last_updated"] = ts
            continue
        
        # check if iqamas changed
        new_iqamas = new_value.get("iqamas")
        old_iqamas = old_value.get("iqamas")

        # check if new_iqamas is None (masjid was attempted but failed to be scraped)
        if new_iqamas is None:
            # copy all values from old data
            new_value["iqamas"] = old_iqamas
            new_value["jumas"] = old_value.get("jumas")
            new_value["last_updated"] = old_value["last_updated"]
            continue

        new_value["last_updated"] = ts

        for new_iqama_key, new_iqama_value in new_iqamas.items():
            old_iqama_value = (old_iqamas or {}).get(new_iqama_key)
            if old_iqama_value is None or new_iqama_value["time"] != old_iqama_value["time"]:
                # iqama changed, add it to changes, unless it's maghrib
                if new_iqama_key != "maghrib":
                    changes[new_key] = True
                new_iqama_value["changed"] = True
                new_iqama_value["changed_on"] = today
            elif old_iqama_value.get("changed_on") is not None:
                # iqama didn't change, copy changed_on from old data
                new_iqama_value["changed_on"] = old_iqama_value.get("changed_on")

        # check if jumas changed
        new_jumas = set(new_value["jumas"])
        old_jumas = set(old_value["jumas"])
        if new_jumas != old_jumas:
            # jumas changed, add it to changes
            changes[new_key] = True
            new_value["jumas_changed"] = True

    # replace old file with new data
    if save_to_file is not None:
        with open(save_to_file, 'w') as f:
            json.dump(new_data, f, indent=4)
    
    # if there are changes return them
    if len(changes.keys()) > 0:
        # return only the masjids that changed
        return {k: v for k, v in new_data["masjids"].items() if k in changes.keys()}

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your s3 triggered function " + name + " ran at " + str(current_time))

    # prepare s3 client
    s3_client = boto3_client('s3')
    bucket_name = os.environ.get('S3_BUCKET')
    if bucket_name is None:
        raise Exception("No S3 bucket set, please set S3_BUCKET environment variable")
    new_file_key = 'data/scraped.json'
    new_file_path = '/tmp/scraped.json'
    old_file_key = 'data/notified.json'
    old_file_path = '/tmp/notified.json'

    def create_empty_old_file():
        with open(old_file_path, 'w') as f:
            json.dump({"masjids": {}}, f)
            
    def upload_old_file():
        s3_client.upload_file(
            Filename=old_file_path,
            Bucket=bucket_name,
            Key=old_file_key
        )

    def download_new_file():
        s3_client.download_file(
            bucket_name,
            new_file_key,
            new_file_path
        )

    def download_old_file():
        s3_client.download_file(
            bucket_name,
            old_file_key,
            old_file_path
        )

    def delete_new_file():
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=new_file_key
        )
 
    def notify_subscribers(changes):
        # get environment variables
        contact_list_name = os.environ.get('CONTACT_LIST_NAME')
        if contact_list_name is None:
            raise Exception("No contact list name set, please set CONTACT_LIST_NAME environment variable")
        email_from = os.environ.get('EMAIL_FROM')
        if email_from is None:
            raise Exception("No email from set, please set EMAIL_FROM environment variable")
        email_template = os.environ.get('EMAIL_TEMPLATE')
        if email_template is None:
            raise Exception("No email template set, please set EMAIL_TEMPLATE environment variable")
        
        ses_client = boto3_client('sesv2')

        # merge existing topics with new topics and return unique topics
        def merge_topics(existing_topics, new_topics):
            unique_tuples = {tuple(d.items()) for d in existing_topics + new_topics}
            return [dict(t) for t in unique_tuples]
        
        # create structure for new topics from changes
        def convert_changes_to_topics():            
            return [{
                "TopicName": topic,
                "DisplayName": masjid["display_name"],
                "Description": "Get email notifications for prayer time updates from this masjid",
                "DefaultSubscriptionStatus": "OPT_OUT"
            } for topic, masjid in changes.items()]
        
        # get contact list from Amazon SES and create or update it with new topics
        def create_or_update_contact_list(new_topics):
            try:
                logger.debug(f"Getting contact list: {contact_list_name}")
                existing_topics = ses_client.get_contact_list(ContactListName=contact_list_name)["Topics"]
                logger.debug(f"Contact list exists: {contact_list_name}, topics: {existing_topics}")
                merged_topics = merge_topics(existing_topics, new_topics)
                logger.debug(f"Merged topics: {merged_topics}")
                ses_client.update_contact_list(ContactListName=contact_list_name, Topics=merged_topics)
                logger.debug(f"Contact list updated: {contact_list_name}, topics: {merged_topics}")
            except ses_client.exceptions.NotFoundException:
                logger.warning(f"Contact list doesn't exist, creating it: {contact_list_name}")
                ses_client.create_contact_list(ContactListName=contact_list_name, Topics=new_topics)
                logger.debug(f"Contact list created: {contact_list_name}, topics: {new_topics}")

        def list_contacts_paginated(topic, next_token):
            kwargs = {
                'ContactListName': contact_list_name,
                'Filter': {
                    'FilteredStatus': 'OPT_IN',
                    'TopicFilter': {
                        'TopicName': topic,
                        'UseDefaultIfPreferenceUnavailable': True
                    }
                },
                'PageSize': 100
            }
            if next_token is not None:
                kwargs["NextToken"] = next_token
            return ses_client.list_contacts(**kwargs)

        def attempt_to_send_email_to_contact(contact, topic, values):
            ses_client.send_email(
                FromEmailAddress=email_from,
                Destination={
                    'ToAddresses': [contact["EmailAddress"]]
                },
                Content={
                    'Template': {
                        'TemplateName': email_template,
                        'TemplateData': json.dumps({
                            "masjid_name": values["display_name"],
                            "masjid_url": values["website"],
                            "masjid_address": values["address"],
                            "iqamas": values["iqamas"],
                            "jumas": values["jumas"],
                            "jumas_changed": values.get("jumas_changed")
                        })
                    }
                },
                ListManagementOptions={
                    'ContactListName': contact_list_name,
                    'TopicName': topic
                }
            )

        def send_email_to_contacts(contacts, topic, values):
            for contact in contacts:
                try:
                    logger.debug(f"Sending email to contact: {contact}")
                    attempt_to_send_email_to_contact(contact, topic, values)
                    logger.info(f"Email sent to contact: {contact}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'TooManyRequestsException':
                        logger.warning(f"Too many requests, retrying in 1 second")
                        time.sleep(1)
                        attempt_to_send_email_to_contact(contact, topic, values)
                        logger.info(f"Email sent to contact: {contact}")
                    elif e.response['Error']['Code'] == 'MessageRejected':
                        logger.warning(f"Message rejected, skipping contact: {contact}")
                    else:
                        raise e

        def iterate_on_topics_and_send_email_to_subscribers():
            # In non-prod envs, we don't want to send emails to all subscribers
            # Instead we send all (reduced) emails for a specific topic to a single email address
            send_all_to = os.environ.get('SEND_ALL_TO')
            for topic, values in changes.items():
                logger.info(f"Topic: {topic}, Values: {values}")
                if send_all_to is not None and send_all_to != '':
                    logger.debug(f"Sending all emails to: {send_all_to}")
                    send_email_to_contacts([{"EmailAddress": send_all_to}], topic, values)
                    continue
                # get contacts for topic
                next_token = None
                while True:
                    # TODO check if it raises 404 error if no more contacts
                    response = list_contacts_paginated(topic, next_token)
                    contacts = response["Contacts"]
                    logger.debug(f"Contacts: {contacts}")
                    if len(contacts) == 0:
                        break
                    send_email_to_contacts(contacts, topic, values)
                    next_token = response.get("NextToken")
                    logger.debug(f"Next token: {next_token}")
                    if next_token is None or next_token == '':
                        break

        new_topics = convert_changes_to_topics()
        create_or_update_contact_list(new_topics)
        iterate_on_topics_and_send_email_to_subscribers()

    # download new file from s3
    download_new_file()
    logger.debug("New file downloaded")
    
    # download old file from s3
    try:
        download_old_file()
        logger.debug("Old file downloaded")
    except ClientError as e:
        code = e.response['Error']['Code']
        # S3 HEAD Object returns 403 if file doesn't exist in some cases
        if code == '403' or code == '404':
            create_empty_old_file()
            logger.debug("Old file not found, created empty one")
        else:
            raise e

    # detect changes
    old_data = read_json(old_file_path)
    new_data = read_json(new_file_path)

    changes = detect_changes(old_data=old_data, new_data=new_data, save_to_file=old_file_path)

    # replace old file with new one
    upload_old_file()
    logger.debug("Old file replaced with new one")

    # notify subscribers of changes if any
    if changes is None:
        logger.info("No changes detected, not counting Maghrib changes")
    else:
        logger.info("Changes detected")
        # notify subscribers
        notify_subscribers(changes)
        logger.debug("Subscribers notified")

    # delete new file
    delete_new_file()
    logger.debug("New file deleted")

    return f"Changes: {changes}"
