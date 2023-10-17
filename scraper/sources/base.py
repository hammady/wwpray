from requests import get as requests_get


class Source:
    def __init__(self, name, url=None, headers = {}):
        self.name = name
        self._headers = headers
        self._url = url

    def request(self):
        if self._url is None:
            raise Exception("No URL set for source: " + self.name)
        response = requests_get(self._url, headers=self._headers)
        response.raise_for_status()
        self._response = response

    def parse(self):
        raise NotImplementedError
