from .bases import HTMLSource


class ICCOSource(HTMLSource):
    def __init__(self):
        super().__init__("ICCO", headers={
            "Accept": "text/html",
        }, url="https://centres.macnet.ca/icco/")
        
    def parse(self):
        soup = super().parse()

        nested_rows = soup.select("#dailyprayertime-2 > table > tr:nth-child(4) tr")

        iqamas = {
            "fajr": {
                "time": soup.select_one("#dailyprayertime-2 > table > tr:nth-child(3) > td.jamah").text.strip()
            },
            "zuhr": {
                "time": nested_rows[0].select_one("td.jamah").text.strip()
            },
            "asr": {
                "time": nested_rows[1].select_one("td.jamah").text.strip()
            },
            "maghrib": {
                "time": nested_rows[2].select_one("td.jamah").text.strip()
            },
            "isha": {
                "time": nested_rows[3].select_one("td.jamah").text.strip()
            },
        }
        # Get jumaa table rows and remove first and last rows
        jumas = [f"{juma.text.strip()}" for juma in soup.select("#text-6 > div > p")][1:-1]
        # Combine each tow rows into one
        jumas = [jumas[i] + " by " + jumas[i+1] for i in range(0, len(jumas), 2)]

        return iqamas, jumas