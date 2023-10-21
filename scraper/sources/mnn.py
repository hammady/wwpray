from .bases import TMASource


class MNNexusSource(TMASource):
    def __init__(self):
        super().__init__()
        self.name = "MNNexus"
        self._url = self._url + "/mnnexus"
        self.display_name = 'Muslim Neighbour Nexus (MNN)'
        self.website = 'https://mnnexus.ca/'
        self.address = '3520 Odyssey Dr, Mississauga, ON L5M 0Y9'
