from bs4 import BeautifulSoup
from .bases import HTMLSource


class AlfarooqSource(HTMLSource):
    def __init__(self):
        super().__init__("Alfarooq", headers={
            "Accept": "text/html",
        }, url="https://www.masjidfarooq.com/",
        timezone="America/Toronto")
        self.display_name = 'Masjid Al-Farooq'
        self.website = 'https://www.masjidfarooq.com/'
        self.address = '935 Eglinton Ave W, Mississauga, ON L5V 1R6'
        self.latitude = 43.586899
        self.longitude = -79.675926
        
    def parse(self):
        soup = super().parse()

        # The table is a flat structure; Sunrise has no td.jamah (colspan=2),
        # so selecting td.jamah yields exactly 5 cells: Fajr, Dhuhr, Asr, Maghrib, Isha
        jamah_cells = soup.select("table.dptTimetable td.jamah")

        iqamas = self.generate_iqamas_output(
            [cell.text.strip() for cell in jamah_cells]
        )

        # Fetch Juma salah times from the monthly timetable page
        monthly_response = self._http_method(
            "https://www.masjidfarooq.com/monthly-timetable/",
            headers=self._headers,
            timeout=(3.05, 6)
        )
        monthly_response.raise_for_status()
        monthly_soup = BeautifulSoup(monthly_response.text, "html.parser")

        # Juma table: figure.wp-block-table > table; title in 1st column, khutbah time in 2nd
        juma_rows = monthly_soup.select("figure.wp-block-table table tbody tr")
        jumas = [
            f"{row.select('td')[0].text.strip()}: {row.select('td')[1].text.strip()}"
            for row in juma_rows
        ]

        return iqamas, jumas
