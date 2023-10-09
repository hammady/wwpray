import os
import datetime
import logging
import json
from requests import get as requests_get
from boto3 import client as boto3_client


# set log level from environment variable, defaulting to WARNING
# valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

class Source:
    def __init__(self, name, url=None, headers = {}):
        self.name = name
        self._headers = headers
        self._url = url

    def request(self):
        if self._url is None:
            raise Exception("No URL set for source: " + self.name)
        response = requests_get(self._url, headers=self._headers)
        response.raise_for_status()
        self._response = response

    def parse(self):
        raise NotImplementedError
    
class TMASource(Source):
    def __init__(self):
        super().__init__("The Masjid App", headers={
            "Accept": "application/json",
        }, url="https://themasjidapp.net")
        
    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        masjid = self._response.json()["masjid"]
        iqamas = {
            "fajr": {
                "time": masjid["fajr"]
            },
            "zuhr": {
                "time": masjid["zuhr"]
            },
            "asr": {
                "time": masjid["asr"]
            },
            "maghrib": {
                "time": masjid["maghrib"]
            },
            "isha": {
                "time": masjid["isha"]
            },
        }
        jumas = [f"{juma['timeDesc']} - {juma['locationDesc']}" for juma in masjid["jumas"]]

        return iqamas, jumas
    
class MNNexusSource(TMASource):
    def __init__(self):
        super().__init__()
        self.name = "MNNexus"
        self._url = self._url + "/mnnexus"


class ShalimarSource(TMASource):
    def __init__(self):
        super().__init__()
        self.name = "Shalimar"
        self._url = self._url + "/shalimar-islamic-centre"


inputs = [
    "MNNexusSource",
    "ShalimarSource",
]


def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your scheduled function " + name + " ran at " + str(current_time))

    response = {"max_jumaas": 0, "masjids": {}}
    for input in inputs:
        klass = getattr(__import__("handler"), input)
        source = klass()
        logger.info(f"Running source: {source.name}")
        source.request()
        iqamas, jumas = source.parse()
        logger.info(f"Iqamas: {iqamas}")
        logger.info(f"Jumas: {jumas}")
        response["masjids"][source.name] = {
            "iqamas": iqamas,
            "jumas": jumas,
        }
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

    return "Success"
