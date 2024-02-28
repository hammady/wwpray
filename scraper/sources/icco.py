from .bases import HTMLSource


class ICCOSource(HTMLSource):
    def __init__(self):
        super().__init__("ICCO", headers={
            "Accept": "text/html",
        }, url="https://centres.macnet.ca/icco/",
        timezone="America/Toronto")
        self.display_name = 'Islamic Community Centre of Ontario (ICCO)'
        self.website = 'https://centres.macnet.ca/icco/'
        self.address = '2550 Dunwin Dr, Mississauga, ON L5L 1T1'
        self.latitude = 43.528470
        self.longitude = -79.681020
        
    def parse(self):
        soup = super().parse()

        class_names = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
        iqamas = self.generate_iqamas_output(
            [value.text.strip() for value in [
                soup.select_one(f".prayer-time.prayer-{name} .prayer-jamaat")
                for name in class_names
            ]]
        )

        rows_selector = "div[data-id='7010618'] > div > div"
        jumas = [row.text.strip().replace('\n', '') for row in soup.select(rows_selector)]
        
        return iqamas, jumas
