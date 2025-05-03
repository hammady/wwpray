from .bases import Source

class DarulTaqwaSource(Source):
    def __init__(self):
        super().__init__(
            "DarulTaqwa",
            url="https://d3uteqio583lem.cloudfront.net/cms/read/en-US",
            timezone="America/Toronto",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer ac830963f4921ead84d48c7fd862dc287c2abc4caecf2ed3",
                "X-tenant": "root"
            },
            http_method='POST',
            request_body='{"query":"{listAzanTimes{data{azaanTime{jumah}}}listIqamaTimes {data{iqamaTime{fajr dhuhr asr maghrib isha jumah}}}}"}'
        )
        self.display_name="Darul Taqwa"
        self.website="https://darultaqwa.ca/"
        self.address="1601 Eglinton Ave W, Mississauga, ON L5M 7C"
        self.latitude=43.572885
        self.longitude=-79.691325

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        payload = self._response.json()
        iqamah_times = payload['data']['listIqamaTimes']['data'][0]['iqamaTime']
        iqamas = self.generate_iqamas_output([
            iqamah_times['fajr'],
            iqamah_times['dhuhr'],
            iqamah_times['asr'],
            iqamah_times['maghrib'],
            iqamah_times['isha']
        ])
        # $.data.listAzanTimes.data[0].azaanTime.jumah
        juma_azan = payload['data']['listAzanTimes']['data'][0]['azaanTime']['jumah']
        jumas = [f"Azaan: {juma_azan}, Iqama: {iqamah_times['jumah']}"]
        return iqamas, jumas