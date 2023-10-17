from .tma import TMASource


class MNNexusSource(TMASource):
    def __init__(self):
        super().__init__()
        self.name = "MNNexus"
        self._url = self._url + "/mnnexus"
