from .bases import HTMLSource


class ArRehmanSource(HTMLSource):
    def __init__(self):
        super().__init__("ARIC", headers={
            "Accept": "text/html",
        }, url="https://aric-icna.ca/",
        timezone="America/Toronto")
        self.display_name = 'Ar-Rehman Islamic Center'
        self.website = 'https://aric-icna.ca/'
        self.address = '6120 Montevideo Rd, Mississauga, ON L5N 3W5'
        
    def parse(self):
        soup = super().parse()
        
        table = soup.select_one("div.et_pb_module.et_pb_code.et_pb_code_0 > div > table > tbody")

        iqamas = self.generate_iqamas_output(
            [
                table.select_one(f"tr:nth-child({index+1}) > td:nth-child(2)").text.strip()
                for index in range(len(self._five_prayers))
            ]
        )

        table = soup.select_one("div.et_pb_module.et_pb_text.et_pb_text_4 > div > table > tbody")

        # Get jumaa table rows after first row
        jumas = [
            f"{tr.select_one('td:nth-child(1)').text.strip()}: " +
            f"Khutbah: {tr.select_one('td:nth-child(2)').text.strip()} - " +
            f"Jammah: {tr.select_one('td:nth-child(3)').text.strip()}"
            for tr in table.select("tr")[1:]
        ]

        return iqamas, jumas
