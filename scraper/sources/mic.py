from .bases import HTMLSource


class MICSource(HTMLSource):
    def __init__(self):
        super().__init__("MIC", headers={
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }, url="https://mici.org/",
        timezone="America/Toronto")
        self.display_name = 'Meadowvale Islamic Centre'
        self.website = 'https://mici.org/'
        self.address = '6508 Winston Churchill Blvd, Mississauga, ON L5N 3W4'
        self.latitude = 43.5809972
        self.longitude = -79.7645107
        
    def parse(self):
        soup = super().parse()

        iqamas_tr = soup.select_one("table#tablepress-6 > tbody > tr")
        iqamas = self.generate_iqamas_output(
            [
                iqamas_tr.select_one(f"td.column-{col}").text.strip() for col in range(2, 7)
            ]
        )

        # jumas are loaded using AJAX, so we need to request a separate page
        self._url = "https://mici.org/wp-admin/admin-ajax.php?action=wp_ajax_ninja_tables_public_action&table_id=513&target_action=get-all-data&default_sorting=old_first"
        self.request()
        json = self._response.json()
        jumas = [
            f"{row['value']['payer']}: {row['value']['khutba']} ({row['value']['imam']})" for row in json
        ]

        return iqamas, jumas
