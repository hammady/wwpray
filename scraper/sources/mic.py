from .bases import HTMLSource


class MICSource(HTMLSource):
    def __init__(self):
        super().__init__("MIC", headers={
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }, url="https://themasjidapp.org/26/prayers",
        timezone="America/Toronto")
        self.display_name = 'Meadowvale Islamic Centre'
        self.website = 'https://mici.org/'
        self.address = '6508 Winston Churchill Blvd, Mississauga, ON L5N 3W4'
        self.latitude = 43.5809972
        self.longitude = -79.7645107
        
    def parse(self):
        soup = super().parse()

        # Find all table rows - there should be 6 rows for the 6 prayers
        table_rows = soup.select("table > tbody > tr")
        
        # Extract iqama times from last column, skipping the 2nd row (Sunrise)
        iqama_times = []
        for i, row in enumerate(table_rows):
            if i == 1:  # Skip Sunrise row (index 1)
                continue
            if i == 6:  # Skip Jumuah row (index 6) - we'll handle it separately
                continue
            cells = row.select("td")
            if len(cells) >= 3:  # Make sure we have at least 3 columns
                iqama_time = cells[-1].text.strip()  # Last column
                iqama_times.append(iqama_time)
        
        iqamas = self.generate_iqamas_output(iqama_times)

        # Extract Jumuah times from the 7th row (index 6) - this row has only 2 columns
        jumas = []
        if len(table_rows) > 6:  # Make sure we have at least 7 rows
            jumuah_row = table_rows[6]
            cells = jumuah_row.select("td")
            if len(cells) >= 2:  # Jumuah row has only 2 columns
                jumuah_times_text = cells[-1].text.strip()  # Last column (2nd column)
                if jumuah_times_text:
                    # Split on commas and clean up each time
                    jumuah_times = [time.strip() for time in jumuah_times_text.split(',')]
                    jumas = [f"Jumuah: {time}" for time in jumuah_times if time]

        return iqamas, jumas
