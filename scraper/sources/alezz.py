from .bases import MasjidBoxSource

class AlEzzSource(MasjidBoxSource):
    def __init__(self):
        super().__init__(
            apikey="JejYcMS7hsOsZTPDk2ZhKOAlW9IyQ6Px",
            masjidbox_id="masjid-al-ezz",
            timezone="America/Toronto"
        )
        self.name = "AlEzz"
        self.display_name = 'Masjid Al-Ezz'
        self.website = 'https://masjidalezz.com/'
        self.address = '10 Falconer Dr #8, Mississauga, ON L5N 3L8'
        self.latitude = 43.592656
        self.longitude = -79.7262345
