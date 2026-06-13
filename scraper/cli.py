# cli to test source scraping

import click
from sources.bases.base import Source


def _format_seconds_utc(seconds, timezone):
    # Convert seconds-since-midnight-UTC back to a human-friendly local time
    if seconds is None:
        return "??:?? (unparsed)"
    offset = Source._get_current_time_in_timezone(timezone).utcoffset().total_seconds()
    local_seconds = int(seconds + offset) % 86400
    hours, remainder = divmod(local_seconds, 3600)
    minutes = remainder // 60
    suffix = "AM" if hours < 12 else "PM"
    hour_12 = hours % 12 or 12
    return f"{hour_12}:{minutes:02d} {suffix}"


@click.command()
@click.option('--source', '-s', required=True, help='Python class name for the source to scrape')
def main(source):
    klass = getattr(__import__("sources"), source)
    source = klass()
    print(f"Scraping {source.name}...")
    source.request()
    iqamas, jumas, jumas_seconds = source.parse()
    print("Iqamas:")
    for name, iqama in iqamas.items():
        formatted = _format_seconds_utc(iqama["seconds_since_midnight_utc"], source._timezone)
        print(f"  {name:8} {formatted}  <-  {iqama['time']}")
    print("Jumas:")
    for juma, seconds in zip(jumas, jumas_seconds):
        print(f"  {_format_seconds_utc(seconds, source._timezone)}  <-  {juma}")

if __name__ == "__main__":
    main()
