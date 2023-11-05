from .bases import TMASource


class MNNexusSource(TMASource):
    def __init__(self):
        super().__init__("America/Toronto", masjid_id=10)
        self.name = "MNNexus"
        self.display_name = 'Muslim Neighbour Nexus (MNN)'
        self.website = 'https://mnnexus.ca/'
        self.address = '3520 Odyssey Dr, Mississauga, ON L5M 0Y9'
