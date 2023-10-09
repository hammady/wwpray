import os
import datetime
import logging
import csv
from requests import get as requests_get

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

    max_jumas = 0
    all_names = []
    all_iqamas = []
    all_jumas = []
    for input in inputs:
        klass = getattr(__import__("handler"), input)
        source = klass()
        all_names.append(source.name)
        logger.info(f"Running source: {source.name}")
        source.request()
        iqamas, jumas = source.parse()
        logger.info(f"Iqamas: {iqamas}")
        logger.info(f"Jumas: {jumas}")
        all_iqamas.append(iqamas)
        all_jumas.append(jumas)
        max_jumas = max(max_jumas, len(jumas))
        logger.debug(f"Max jumas: {max_jumas}")
    
    # write to csv
    header = ["fajr", "zuhr", "asr", "maghrib", "isha"]
    with open("output.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name"] + header + [f"juma {i+1}" for i in range(max_jumas)])
        for name, iqamas, jumas in zip(all_names, all_iqamas, all_jumas):
            jumas_arr = [f"{juma[0]} at {juma[1]}" for juma in jumas]
            # pad jumas array to max length
            jumas_arr += [""] * (max_jumas - len(jumas))
            writer.writerow([name] + [iqamas[key] for key in header] + jumas_arr)
    
    return True
