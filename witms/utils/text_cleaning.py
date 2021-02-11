from datetime import datetime as dt


def replace_smart_quotes(text):
    return (
        text.replace(u"\u2018", "'")
        .replace(u"\u2019", "'")
        .replace(u"\u201c", '"')
        .replace(u"\u201d", '"')
    )


def parse_timestamp(timestamp: str) -> str:
    date_format = "%Y-%m-%dT%H:%M:%S UTC"
    try:
        unix_timestamp = int(timestamp)
    except ValueError:
        try:
            # Handles dates in the format  Sat 30 Jan 2021 15.40 GMT
            date = dt.strptime(str(timestamp), "%a %d %b %Y %H.%M %Z")
            return date.strftime(date_format)
        except ValueError:
            return timestamp
    else:
        try:
            return dt.utcfromtimestamp(unix_timestamp).strftime(date_format)
        except ValueError:
            # Handles timestamps in miliseconds
            ts_secs = unix_timestamp / 1000
            return dt.utcfromtimestamp(ts_secs).strftime(date_format)
