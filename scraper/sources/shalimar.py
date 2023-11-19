from .bases import TMASource


class ShalimarSource(TMASource):
    def __init__(self):
        super().__init__("America/Toronto", masjid_id=7673)
        self.name = "Shalimar"
        self.display_name = 'Shalimar Islamic Centre'
        self.website = 'https://www.shalimarislamiccentre.ca/'
        self.address = '79-3024 Cedarglen Gate, Mississauga, ON, L5C 4S3'
        self.latitude = 43.558650
        self.longitude = -79.642110
