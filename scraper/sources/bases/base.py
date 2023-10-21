from requests import get as requests_get


class Source:
    def __init__(self, name, url=None, headers = {}):
        self.name = name
        self.display_name = None
        self.website = None
        self.address = None
        self._headers = headers
        self._url = url
        self._counter_labels = [
            'First', 'Second', 'Third', 'Fourth', 'Fifth',
            'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']

    def request(self):
        if self._url is None:
            raise Exception("No URL set for source: " + self.name)
        response = requests_get(
            self._url,
            headers=self._headers,
            timeout=(3.05, 2)) # 3.05 seconds to connect, 2 seconds to read
        response.raise_for_status()
        self._response = response

    def parse(self):
        raise NotImplementedError
