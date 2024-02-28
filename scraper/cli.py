# cli to test source scraping

import click
from sources import *

@click.command()
@click.option('--source', '-s', required=True, help='Python class name for the source to scrape')
def main(source):
    klass = getattr(__import__("sources"), source)
    source = klass()
    print(f"Scraping {source.name}...")
    source.request()
    iqamas, jumas = source.parse()
    print(f"Iqamas: {iqamas}")
    print(f"Jumas: {jumas}")

if __name__ == "__main__":
    main()
