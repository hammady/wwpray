from .base import Source


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
    
