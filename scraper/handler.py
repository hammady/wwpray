import os
import datetime
import logging
import json
import traceback
from boto3 import client as boto3_client
from tenacity import retry, stop_after_attempt, wait_fixed

# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your scheduled function " + name + " ran at " + str(current_time))

    source_class_names = os.environ.get('SOURCES')
    if source_class_names is None:
        raise Exception("No SOURCES set, please set SOURCES environment variable")
    source_class_names = source_class_names.split(",")

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    def process_source(source):
        logger.info(f"Running source: {source.name}")
        source.request()
        return source.parse()

    response = {"max_jumaas": 0, "masjids": {}}
    processed = 0
    for source_class_name in source_class_names:
        klass = getattr(__import__("sources"), source_class_name)
        source = klass()
        iqamas = None
        jumas = None
        try:
            iqamas, jumas = process_source(source)
            processed += 1
        except Exception:
            logger.error(f"Failed to process source {source.name}: {traceback.format_exc()}")
            continue
        finally:
            response["masjids"][source.name] = {
                "iqamas": iqamas,
                "jumas": jumas,
            }            
        logger.info(f"Iqamas: {iqamas}")
        logger.info(f"Jumas: {jumas}")
        response["max_jumaas"] = max(response["max_jumaas"], len(jumas))
        logger.debug(f"Max jumas: {response['max_jumaas']}")
    
    # write response to json file
    json_file_path = "/tmp/output.json"
    with open(json_file_path, "w") as jsonfile:
        json.dump(response, jsonfile, indent=4)

    # upload to s3
    s3_client = boto3_client('s3')
    bucket_name = os.environ.get('S3_BUCKET')
    if bucket_name is None:
        raise Exception("No S3 bucket set, please set S3_BUCKET environment variable")
    s3_client.upload_file(
        Filename=json_file_path,
        Bucket=bucket_name,
        Key='data/scraped.json'
    )

    return f"Scraped {processed} out of {len(source_class_names)} sources"
