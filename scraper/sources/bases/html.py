from .base import Source
from bs4 import BeautifulSoup


class HTMLSource(Source):
    def __init__(self, name, url, timezone, headers):
        super().__init__(name, url=url, timezone=timezone, headers=headers)

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        return BeautifulSoup(self._response.text, "html.parser")
