from .bases import HTMLSource


class AlfarooqSource(HTMLSource):
    def __init__(self):
        super().__init__("Alfarooq", headers={
            "Accept": "text/html",
        }, url="https://www.masjidfarooq.com/")
        
    def parse(self):
        soup = super().parse()

        nested_rows = soup.select("table.dptTimetable > tr:nth-child(4) > tr")

        iqamas = {
            "fajr": {
                "time": soup.select_one("table.dptTimetable > tr:nth-child(3) > td.jamah").text.strip()
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

        jumas = [f"{label} Prayer: {value.text.strip()}" for value, label in zip(
            nested_rows[4].select("td.jamah > span"),
            self._counter_labels
        )]

        return iqamas, jumas
