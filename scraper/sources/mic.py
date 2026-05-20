from .bases import TMASource


class MICSource(TMASource):
    def __init__(self):
        super().__init__("America/Toronto", masjid_id=26)
        self.name = "MIC"
        self.display_name = 'Meadowvale Islamic Centre'
        self.website = 'https://mici.org/'
        self.address = '6508 Winston Churchill Blvd, Mississauga, ON L5N 3W4'
        self.latitude = 43.5809972
        self.longitude = -79.7645107
