from .masjidbox import MasjidBoxSource

class ISNACanadaSource(MasjidBoxSource):
    def __init__(self):
        super().__init__(
            apikey="JejYcMS7hsOsZTPDk2ZhKOAlW9IyQ6Px",
            xkey="GbtTDHCUjOx4WNJjKsKHW",
            xfrom="https://www.isnacanada.com"
        )
        self.name = "ISNACanada"
