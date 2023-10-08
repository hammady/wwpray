import os
import datetime
import logging
from requests import get

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
        response = get(self._url, headers=self._headers)
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
            "fajr": masjid["fajr"],
            "zuhr": masjid["zuhr"],
            "asr": masjid["asr"],
            "maghrib": masjid["maghrib"],
            "isha": masjid["isha"],
        }
        jumas = [(juma["timeDesc"], juma["locationDesc"]) for juma in masjid["jumas"]]

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

    for input in inputs:
        klass = getattr(__import__("handler"), input)
        source = klass()
        logger.info("Running source: " + source.name)
        source.request()
        iqamas, jumas = source.parse()
        logger.info(f"Iqamas: {iqamas}")
        logger.info(f"Jumas: {jumas}")
    
    return True
