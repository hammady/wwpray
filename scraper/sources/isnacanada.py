from .bases import MasjidBoxSource

class ISNACanadaSource(MasjidBoxSource):
    def __init__(self):
        super().__init__(
            apikey="JejYcMS7hsOsZTPDk2ZhKOAlW9IyQ6Px",
            masjidbox_id="isna-canada",
            timezone="America/Toronto"
        )
        self.name = "ISNACanada"
        self.display_name = 'ISNA Canada - ICC'
        self.website = 'https://www.isnacanada.com/'
        self.address = '2200 S Sheridan Way, Mississauga, ON L5J 2M4'
