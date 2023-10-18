from .bases import MasjidBoxSource

class DarFoundationSource(MasjidBoxSource):
    def __init__(self):
        super().__init__(
            apikey="JejYcMS7hsOsZTPDk2ZhKOAlW9IyQ6Px",
            masjidbox_id="dar-foundation",
            timezone="America/Toronto"
        )
        self.name = "DarFoundation"
