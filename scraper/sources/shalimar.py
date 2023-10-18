from .bases import TMASource


class ShalimarSource(TMASource):
    def __init__(self):
        super().__init__()
        self.name = "Shalimar"
        self._url = self._url + "/shalimar-islamic-centre"

