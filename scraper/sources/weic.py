from .bases import HTMLSource


class WEICSource(HTMLSource):
    def __init__(self):
        super().__init__("WestEndIslamicCenter", headers={
            "Accept": "text/html",
        }, url="https://weicenter.ca/",
        timezone="America/Toronto")
        self.display_name = 'West End Islamic Center'
        self.website = 'https://weicenter.ca/'
        self.address = '12,13-4161 Sladeview Crescent, Mississauga, ON L5L 5R3'
        self.latitude = 43.530700
        self.longitude = -79.718800
        
    def parse(self):
        soup = super().parse()

        tbody = soup.select_one("table.dptTimetable")
        nested_rows = tbody.select_one("tr:nth-child(4)")

        zuhr_spans = nested_rows.select("tr")[0].select("td.jamah > span")
        if len(zuhr_spans) == 0:
            # today is not Friday, this is a single value
            zuhr_tag = nested_rows.select("tr")[0].select_one("td.jamah")
        else:
            # today is Friday, jumas will be listed instead of Zuhr, take the first span
            zuhr_tag = zuhr_spans[0]

        iqamas = self.generate_iqamas_output(
            [value.text.strip() for value in [
                tbody.select_one("tr:nth-child(3) > td.jamah"),
                zuhr_tag,
                nested_rows.select("tr")[1].select_one("td.jamah"),
                nested_rows.select("tr")[2].select_one("td.jamah"),
                nested_rows.select("tr")[3].select_one("td.jamah")
            ]]
        )

        # Get the tbody after the h1 containing "Friday"
        tbody = soup.select_one("h1:-soup-contains('Friday')").find_next("table")

        # Get all trs in the tbody, and join the text of all tds
        jumas = [" - ".join([td.text.strip() for td in tr.select("td")]) for tr in tbody.select("tr")]

        return iqamas, jumas
