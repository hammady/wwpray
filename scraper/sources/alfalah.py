from .bases import MasjidalSource


class AlfalahSource(MasjidalSource):
    def __init__(self):
        super().__init__(masjid_id='EdoleqK7', extra_jumas=['2:30PM'])
        self.name = 'AlfalahICNA'
