import os
import datetime
import logging
import json
from boto3 import client as boto3_client


# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your httpApi function " + name + " ran at " + str(current_time))

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

    def get_valid_topics():
        return [
            topic["TopicName"]
            for topic in ses_client.get_contact_list(ContactListName=contact_list_name)["Topics"]
        ]
        
    def validate_topics(topics):
        valid_topics = get_valid_topics()
        for topic in topics:
            if topic not in valid_topics:
                return False
        return True
    
    # get query string parameters
    qs_params = event.get("queryStringParameters")
    if qs_params is None:
        return {"statusCode": 400, "body": "No query string parameters provided"}
    email = qs_params.get("email")
    if email is None:
        return {"statusCode": 400, "body": "No email provided"}
    topics = qs_params.get("topics")
    if topics is None:
        return {"statusCode": 400, "body": "No topics provided"}
    new_topics = topics.split(",")
    if validate_topics(new_topics) is False:
        return {"statusCode": 400, "body": "Invalid topics provided"}
    logger.info(f"Email: {email}, Topics: {new_topics}")
    
    def subscribe_contact_to_topics():
        try:
            # try to get contact
            logger.debug(f"Getting contact with email: {email}")
            contact = ses_client.get_contact(
                ContactListName=contact_list_name,
                EmailAddress=email
            )
            logger.debug(f"Contact: {contact}")
            # get existing opt-in topics
            contact_topics = [
                topic["TopicName"]
                for topic in contact["TopicPreferences"]
                if topic["SubscriptionStatus"] == "OPT_IN"
            ]
            logger.debug(f"Contact opt-in topics: {contact_topics}")
            # merge existing opt-in topics with new topics
            merged_topics = list(set(contact_topics + new_topics))
            logger.debug(f"Merged topics: {merged_topics}")
            # generate new topic preferences
            new_topic_preferences = [
                {
                    "TopicName": topic,
                    "SubscriptionStatus": "OPT_IN"
                }
                for topic in merged_topics
            ]
            # update contact
            ses_client.update_contact(
                ContactListName=contact_list_name,
                EmailAddress=email,
                UnsubscribeAll=False,
                TopicPreferences=new_topic_preferences
            )
            logger.info(f"Updated contact with email: {email} and topics: {new_topic_preferences}")
            # return newly added topics only
            return list(set(merged_topics) - set(contact_topics))
        except ses_client.exceptions.NotFoundException:
            logger.debug(f"Contact with email: {email} not found, creating new contact")
            # create contact with new topics
            new_topic_preferences = [
                {
                    "TopicName": topic,
                    "SubscriptionStatus": "OPT_IN"
                }
                for topic in new_topics
            ]
            ses_client.create_contact(
                ContactListName=contact_list_name,
                EmailAddress=email,
                UnsubscribeAll=False,
                TopicPreferences=new_topic_preferences
            )
            logger.info(f"Created contact with email: {email} and topics: {new_topic_preferences}")
            return new_topics

    def send_confirmation_email(topics):
        logger.info(f"Sending confirmation email to {email} for topics: {topics}")
        ses_client.send_email(
            FromEmailAddress=email_from,
            Destination={
                'ToAddresses': [email]
            },
            Content={
                'Template': {
                    'TemplateName': email_template,
                    'TemplateData': json.dumps({
                        "topics": topics
                    })
                }
            },
            ListManagementOptions={
                'ContactListName': contact_list_name
            }
        )        

    # subscribe contact to topics
    try:
        subscribed_topics = subscribe_contact_to_topics()
    except ses_client.exceptions.BadRequestException as e:
        logger.error(f"BadRequestException: {e}")
        return {"statusCode": 400, "body": "Invalid email provided"}
    
    if len(subscribed_topics) > 0:
        # send confirmation email
        send_confirmation_email(subscribed_topics)
        message = f"Succesfully subscribed to new topics. A confirmation email has been sent to {email}."
    else:
        message = "Already subscribed to all topics."

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": message,
            "topics": subscribed_topics
        })
    }
