# cli to test source scraping

import click
from sources.bases.base import Source
from sources.bases.html import HTMLSource


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
@click.option('--dump-html', '-d', is_flag=True,
              help='For HTML sources, save the fetched page to <SourceName>.html '
                   'for debugging (local only; the serverless filesystem is read-only).')
def main(source, dump_html):
    klass = getattr(__import__("sources"), source)
    source = klass()
    source.dump_html = dump_html
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

    if dump_html:
        if isinstance(source, HTMLSource):
            print(f"Dumped fetched HTML to {source.name}.html")
        else:
            print("--dump-html ignored: this source does not fetch HTML")

if __name__ == "__main__":
    main()
