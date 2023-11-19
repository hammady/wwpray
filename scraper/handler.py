import os
import datetime
import logging
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        iqamas, jumas = source.parse()
        return source, iqamas, jumas

    # Results objects below are manipulated in the main thread, so we don't need to worry about locking
    response = {"masjids": {}}
    processed = 0

    # Run each source in a separate thread
    with ThreadPoolExecutor() as executor:
        futures = []
        for source_class_name in sorted(source_class_names):
            klass = getattr(__import__("sources"), source_class_name)
            source = klass()
            # Initialize the response object with metadata, in case the thread fails
            response["masjids"][source.name] = {
                "display_name": source.display_name,
                "website": source.website,
                "address": source.address,
                "latitude": source.latitude,
                "longitude": source.longitude
            }
            # Submit the thread to the executor which will be run immediately
            futures.append(executor.submit(process_source, source))

        # Generate a callback for each thread to be called when the thread is done (no order guaranteed)
        for future in as_completed(futures):
            try:
                # Get the result of the thread, or raise an exception if the thread failed
                source, iqamas, jumas = future.result()
                processed += 1
                response["masjids"][source.name]["iqamas"] = iqamas
                response["masjids"][source.name]["jumas"] = jumas
                logger.info(f"[{source.name}] Iqamas: {iqamas}. Jumas: {jumas}")
            except Exception:
                logger.error(f"Failed to process source: {traceback.format_exc()}")
                continue

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
