import os
import datetime
import logging
import json
from boto3 import client as boto3_client
from urllib.parse import quote_plus, urlparse, parse_qs, urlunparse


# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your httpApi function " + name + " ran at " + str(current_time))

    def respond_with(status_code, message = '', topics = []):
        def respond_with_html():
            logger.debug(f"Returning HTML response with status code: {status_code}.")
            return {
                "statusCode": status_code,
                "headers": {
                    "Content-Type": "text/html"
                },
                "body": f"<html><body><p>{message}</p><p>Topics: {','.join(topics)}</p></body></html>"
            }
        
        def respond_with_json():
            logger.debug(f"Returning JSON response with status code: {status_code}.")
            return {
                "statusCode": status_code,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": message, "topics": topics})
            }

        def respond_with_redirect(url):
            logger.debug(f"Returning redirect response with url: {url}.")
            return {
                "statusCode": 302,
                "headers": {
                    "Location": url
                }
            }
        
        headers = event.get("headers")
        if headers is not None:
            accept_header = headers.get("accept") or headers.get("Accept")
            referer_header = headers.get("referer") or headers.get("Referer")
            if ['application/json', 'text/json'].count(accept_header) > 0:
                return respond_with_json()
            elif referer_header is not None:
                # validate referer header and append message and topics to query string
                referer = urlparse(referer_header)
                if referer.netloc == '':
                    logger.error(f"Invalid referer header: {referer_header}")
                    return respond_with_html()
                qs_arr = parse_qs(referer.query)
                qs_arr["message"] = [quote_plus(message)]
                qs_arr["topics"] = [','.join(topics)]
                qs_str = '&'.join([f"{key}={value[0]}" for key, value in qs_arr.items()])
                return respond_with_redirect(urlunparse(referer._replace(query=qs_str)))
        
        return respond_with_html()
    
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
        contact_list = ses_client.get_contact_list(ContactListName=contact_list_name)
        topics = contact_list.get("Topics", [])
        return [topic["TopicName"] for topic in topics]
        
    def validate_topics(topics):
        valid_topics = get_valid_topics()
        for topic in topics:
            if topic not in valid_topics:
                return False
        return True
    
    # get query string parameters
    qs_params = event.get("queryStringParameters")
    if qs_params is None:
        return respond_with(400, message="No query string parameters provided.")
    email = qs_params.get("email")
    if email is None:
        return respond_with(400, message="No email provided.")
    logger.info(f"Email: {email}")
    topics = qs_params.get("topics")
    if topics is None:
        return respond_with(400, message="No topics provided.")
    logger.info(f"Topics: {topics}")
    new_topics = topics.split(",")
    if validate_topics(new_topics) is False:
        return respond_with(400, message="Invalid topics provided.")
    
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
                for topic in contact.get("TopicPreferences", [])
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
        return respond_with(400, message="Invalid email provided.")
    
    if len(subscribed_topics) > 0:
        # send confirmation email
        send_confirmation_email(subscribed_topics)
        message = f"Successfully subscribed to new topics. A confirmation email has been sent to {email}."
    else:
        message = "Already subscribed to all topics."

    return respond_with(200, message=message, topics=subscribed_topics)
