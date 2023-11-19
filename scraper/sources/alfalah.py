from .bases import MasjidalSource


class AlfalahSource(MasjidalSource):
    def __init__(self):
        super().__init__(masjid_id='EdoleqK7', extra_jumas=['2:30PM'], timezone='America/Toronto')
        self.name = 'AlfalahICNA'
        self.display_name = 'Al Falah Islamic Centre'
        self.website = 'https://alfalahcentre.ca/'
        self.address = '391 Burnhamthorpe Rd E, Oakville, ON L6H 7B4'
        self.latitude = 43.503690
        self.longitude = -79.736310
