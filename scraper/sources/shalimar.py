from .bases import TMASource


class ShalimarSource(TMASource):
    def __init__(self):
        super().__init__("America/Toronto")
        self.name = "Shalimar"
        self._url = self._url + "/shalimar-islamic-centre"
        self.display_name = 'Shalimar Islamic Centre'
        self.website = 'https://www.shalimarislamiccentre.ca/'
        self.address = '79-3024 Cedarglen Gate, Mississauga, ON, L5C 4S3'
