import os
import datetime
import logging
import email
from boto3 import client as boto3_client


# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your s3 triggered function " + name + " ran at " + str(current_time))

    # prepare s3 client
    s3_client = boto3_client('s3')

    bucket_name = os.environ.get('S3_BUCKET')
    if bucket_name is None:
        raise Exception("No S3 bucket set, please set S3_BUCKET environment variable")

    # prepare ses client
    ses_client = boto3_client('sesv2')

    email_from = os.environ.get('EMAIL_FROM')
    if email_from is None:
        raise Exception("No email from set, please set EMAIL_FROM environment variable")
    email_to = os.environ.get('EMAIL_TO')
    if email_to is None:
        raise Exception("No email to set, please set EMAIL_TO environment variable")
    
    def download_message(message_id):
        message_key = f"mail/{message_id}"
        message_path = f"/tmp/{message_id}"
        s3_client.download_file(
            bucket_name,
            message_key,
            message_path
        )
        logger.debug(f"Downloaded message {message_id}")
        with open(message_path) as f:
            return f.read()

    def forward_message(message):
        # parse MIME message
        parsed_message = email.message_from_string(message)
        # replace From header (SES will reject messages with a From header that is not verified)
        original_from = parsed_message["From"]
        parsed_message.replace_header("From", email_from)
        # remove Return-Path header
        del parsed_message["Return-Path"]
        # add Reply-To header
        parsed_message.add_header("Reply-To", original_from)
        # prepend [Forwarded] and append original From to Subject
        parsed_message.replace_header("Subject", f"[Forwarded] {parsed_message['Subject']} [replying to {original_from}]")

        ses_client.send_email(
            Destination={
                'ToAddresses': [email_to]
            },
            Content={
                'Raw': {
                    'Data': parsed_message.as_string()
                }
            }
        )
        logger.debug(f"Forwarded message to {email_to}")

    def process_records(records):
        for record in records:
            # extract message attributes
            mail = record["ses"]["mail"]
            message_id = mail["messageId"]
            source = mail["source"]
            logger.info(f"Received message {message_id} from {source}")
            # download message from s3
            message = download_message(message_id)
            # forward message to admin using ses
            forward_message(message)

    records = event["Records"]
    logger.debug(f"Received {len(records)} records")
    process_records(records)

    return "Success!"
