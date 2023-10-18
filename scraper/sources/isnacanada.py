from .bases import MasjidBoxSource

class ISNACanadaSource(MasjidBoxSource):
    def __init__(self):
        super().__init__(
            apikey="JejYcMS7hsOsZTPDk2ZhKOAlW9IyQ6Px",
            masjidbox_id="isna-canada",
            timezone="America/Toronto"
        )
        self.name = "ISNACanada"
