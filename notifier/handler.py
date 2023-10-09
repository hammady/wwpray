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
    changed, changes = detect_changes()

    if not changed:
        logger.info("No changes detected")
    else:
        logger.info("Changes detected")
        # notify subscribers of changes if any
        # TODO: implement notification logic

        # replace old file with new one
        replace_old_with_new()
        logger.debug("Old file replaced with new one")

    # add last updated timestamp
    create_last_updated_timestamp()
    logger.debug("Last updated timestamp created")

    # delete new file
    delete_new_file()
    logger.debug("New file deleted")

    return f"Changed: {changed}"
