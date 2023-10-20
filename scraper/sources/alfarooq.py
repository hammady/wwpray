from .bases import HTMLSource


class AlfarooqSource(HTMLSource):
    def __init__(self):
        super().__init__("Alfarooq", headers={
            "Accept": "text/html",
        }, url="https://www.masjidfarooq.com/")
        
    def parse(self):
        soup = super().parse()

        nested_rows = soup.select("table.dptTimetable > tr:nth-child(4) > tr")

        if len(nested_rows) == 5:
            # today is not Friday, jumas will be listed in the 5th row
            jumas_row = 4
        else:
            # today is Friday, jumas will be listed instead of Zuhr
            jumas_row = 0

        spans = nested_rows[jumas_row].select("td.jamah > span")

        if jumas_row == 4:
            zuhr_tag = nested_rows[0].select_one("td.jamah")
        else:
            zuhr_tag = spans[0]

        iqamas = {
            "fajr": {
                "time": soup.select_one("table.dptTimetable > tr:nth-child(3) > td.jamah").text.strip()
            },
            "zuhr": {
                "time": zuhr_tag.text.strip()
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
            spans, self._counter_labels
        )]

        return iqamas, jumas
