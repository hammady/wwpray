import os
import datetime
import logging
import json
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

    def check_if_old_file_exists():
        try:
            s3_client.head_object(Bucket=bucket_name, Key=old_file_key)
            return True
        except ClientError:
            return False
    
    def replace_old_with_new():
        s3_client.upload_file(
            Filename=new_file_path,
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

    def create_last_updated_timestamp():
        # generate UTC timestamp in ISO format
        ts = datetime.datetime.utcnow().isoformat()
        s3_client.put_object(
            Bucket=bucket_name,
            Key='data/last_updated.txt',
            Body=ts
        )

    def detect_changes():
        old_data = read_json(old_file_path)
        logger.debug(f"Old data: {old_data}")
        new_data = read_json(new_file_path)
        logger.debug(f"New data: {new_data}")

        changes = {}

        # iterate through masjids in new data
        for new_key, new_value in new_data["masjids"].items():
            # check if masjid doesn't exist in old data
            old_value = old_data["masjids"].get(new_key)
            if old_value is None:
                # masjid doesn't exist in old data, add it to changes
                changes[new_key] = True
                continue
            
            # check if iqamas changed
            new_iqamas = new_value["iqamas"]
            old_iqamas = old_value["iqamas"]
            for new_iqama_key, new_iqama_value in new_iqamas.items():
                old_iqama_value = old_iqamas.get(new_iqama_key)
                if old_iqama_value is None or new_iqama_value["time"] != old_iqama_value["time"]:
                    # iqama changed, add it to changes
                    changes[new_key] = True
                    new_iqama_value["changed"] = True

        # write back the new file if there are changes
        if len(changes.keys()) > 0:
            with open(new_file_path, 'w') as f:
                json.dump(new_data, f, indent=4)
            # filter and return new_data["masjids"] by changes
            return {k: v for k, v in new_data["masjids"].items() if k in changes.keys()}
    
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
                "DisplayName": f"{topic} Masjid",
                "Description": "Get email notifications for prayer time updates from this masjid",
                "DefaultSubscriptionStatus": "OPT_OUT"
            } for topic in changes.keys()]
        
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
                logger.debug(f"Contact list doesn't exist, creating it: {contact_list_name}")
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

        def send_email_to_contacts(contacts, topic, values):
            for contact in contacts:
                logger.debug(f"Sending email to contact: {contact}")
                ses_client.send_email(
                    FromEmailAddress=email_from,
                    Destination={
                        'ToAddresses': [contact["EmailAddress"]]
                    },
                    Content={
                        'Template': {
                            'TemplateName': email_template,
                            'TemplateData': json.dumps({
                                "masjid": topic,
                                "iqamas": values["iqamas"]
                            })
                        }
                    },
                    ListManagementOptions={
                        'ContactListName': contact_list_name,
                        'TopicName': topic
                    }
                )

        def iterate_on_topics_and_send_email_to_subscribers():
            for topic, values in changes.items():
                logger.info(f"Topic: {topic}, Values: {values}")
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
    
    # check if old file exists and create it if not
    if not check_if_old_file_exists():
        logger.debug("No old file found, creating one")
        # copy new file to old file to cover the initial case
        replace_old_with_new()

    # download old file from s3
    download_old_file()
    logger.debug("Old file downloaded")

    # detect changes
    changes = detect_changes()

    # notify subscribers of changes if any
    if changes is None:
        logger.info("No changes detected")
        # add last updated timestamp so that it shows a recent check even if not updated
        create_last_updated_timestamp()
        logger.debug("Last updated timestamp created")
    else:
        logger.info("Changes detected")

        # replace old file with new one
        replace_old_with_new()
        logger.debug("Old file replaced with new one")

        # add last updated timestamp
        create_last_updated_timestamp()
        logger.debug("Last updated timestamp created")

        # notify subscribers
        notify_subscribers(changes)
        logger.debug("Subscribers notified")

    # delete new file
    delete_new_file()
    logger.debug("New file deleted")

    return f"Changes: {changes}"
