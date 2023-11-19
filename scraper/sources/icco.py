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

        nested_rows = soup.select("#dailyprayertime-2 > table > tr:nth-child(4) tr")

        iqamas = self.generate_iqamas_output(
            [value.text.strip() for value in [
                soup.select_one("#dailyprayertime-2 > table > tr:nth-child(3) > td.jamah"),
                nested_rows[0].select_one("td.jamah"),
                nested_rows[1].select_one("td.jamah"),
                nested_rows[2].select_one("td.jamah"),
                nested_rows[3].select_one("td.jamah")
            ]]
        )

        # Get jumaa table rows and remove first row
        jumas = [f"{juma.text.strip()}" for juma in soup.select("#text-6 > div > p")][1:]
        # Combine each tow rows into one, discarding the last row if there is an odd number of rows
        jumas = [jumas[i] + " by " + jumas[i+1] for i in range(0, len(jumas)//2*2, 2)]

        return iqamas, jumas
