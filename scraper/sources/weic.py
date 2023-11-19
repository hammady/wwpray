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

        tbody = soup.select_one("#post-1851 > div > div > div > div.et_pb_section.et_pb_section_1.et_section_regular > div.et_pb_with_border.et_pb_row.et_pb_row_0 > div > div.et_pb_with_border.et_pb_module.et_pb_text.et_pb_text_0.et_pb_text_align_left.et_pb_bg_layout_light > div > table > tbody > tr:nth-child(2) > td > b > table")
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

        tbody = soup.select_one("#post-1851 > div > div > div > div.et_pb_section.et_pb_section_1.et_section_regular > div.et_pb_with_border.et_pb_row.et_pb_row_0 > div > div.et_pb_with_border.et_pb_module.et_pb_text.et_pb_text_1.et_pb_text_align_left.et_pb_bg_layout_light > div > table")

        # Get all trs in the tbody, and join the text of all tds
        jumas = [" - ".join([td.text.strip() for td in tr.select("td")]) for tr in tbody.select("tr")]

        return iqamas, jumas
