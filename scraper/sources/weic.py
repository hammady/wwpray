from .bases import HTMLSource


class WEICSource(HTMLSource):
    def __init__(self):
        super().__init__("WestEndIslamicCenter", headers={
            "Accept": "text/html",
        }, url="https://weicenter.ca/")
        
    def parse(self):
        soup = super().parse()

        tbody = soup.select_one("#post-1851 > div > div > div > div.et_pb_section.et_pb_section_1.et_section_regular > div.et_pb_with_border.et_pb_row.et_pb_row_0 > div > div.et_pb_with_border.et_pb_module.et_pb_text.et_pb_text_0.et_pb_text_align_left.et_pb_bg_layout_light > div > table > tbody > tr:nth-child(2) > td > b > table")
        nested_rows = tbody.select_one("tr:nth-child(4)")

        iqamas = {
            "fajr": {
                "time": tbody.select_one("tr:nth-child(3) > td.jamah").text.strip()
            },
            "zuhr": {
                "time": nested_rows.select("tr")[0].select_one("td.jamah").text.strip()
            },
            "asr": {
                "time": nested_rows.select("tr")[1].select_one("td.jamah").text.strip()
            },
            "maghrib": {
                "time": nested_rows.select("tr")[2].select_one("td.jamah").text.strip()
            },
            "isha": {
                "time": nested_rows.select("tr")[3].select_one("td.jamah").text.strip()
            },
        }

        tbody = soup.select_one("#post-1851 > div > div > div > div.et_pb_section.et_pb_section_1.et_section_regular > div.et_pb_with_border.et_pb_row.et_pb_row_0 > div > div.et_pb_with_border.et_pb_module.et_pb_text.et_pb_text_1.et_pb_text_align_left.et_pb_bg_layout_light > div > table")

        # Get all trs in the tbody, and join the text of all tds
        jumas = [" - ".join([td.text.strip() for td in tr.select("td")]) for tr in tbody.select("tr")]

        return iqamas, jumas