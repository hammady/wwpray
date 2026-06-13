from .base import Source
from bs4 import BeautifulSoup


class HTMLSource(Source):
    def __init__(self, name, url, timezone, headers):
        super().__init__(name, url=url, timezone=timezone, headers=headers)

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        text = self._response.text
        # Optionally dump the fetched HTML to disk for local debugging. Disabled
        # by default because the serverless/Lambda filesystem is read-only and
        # writing would crash. Enabled via the cli's --dump-html flag.
        if self.dump_html:
            with open(f"{self.name}.html", "w", encoding="utf-8") as f:
                f.write(text)
        return BeautifulSoup(text, "html.parser")
