from .bases import MasjidalSource


class HICCSource(MasjidalSource):
    def __init__(self):
        super().__init__(masjid_id='0Lb747Ao', extra_jumas=['3:30 PM'], timezone='America/Toronto')
        self.name = 'HICC'
        self.display_name = 'HICC Masjid - Muslim Association of Milton'
        self.website = 'https://miltonmasjid.com/'
        self.address = '4269 Regional Road 25, Oakville, ON L6M 4E9'
        self.latitude = 43.4570552
        self.longitude = -79.8046367
