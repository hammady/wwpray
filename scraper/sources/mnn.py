from .bases import HTMLSource


class MNNexusSource(HTMLSource):
    def __init__(self):
        super().__init__("MNNexus", headers={
            "Accept": "text/html",
        }, url="https://jangda.ca/mnnptcovid.php",
        timezone="America/Toronto")
        self.display_name = 'Muslim Neighbour Nexus (MNN)'
        self.website = 'https://mnnexus.ca/'
        self.address = '3520 Odyssey Dr, Mississauga, ON L5M 0Y9'
        self.latitude = 43.535220
        self.longitude = -79.724570

    def parse(self):
        soup = super().parse()

        tds = soup.select("body table tr td.time")
        del tds[1] # remove sunrise
        iqamas = self.generate_iqamas_output(
            [value.text.strip() for value in tds]
        )

        jumas = [
            f"MNN Masjid {juma.text.strip()}" for juma in soup.select("div.mnn-jumas div.juma")
        ] + [
            f"Churchill Meadows Comm Ctr {juma.text.strip()}" for juma in soup.select("div.comm-center-jumas div.juma")
        ]

        return iqamas, jumas