from datetime import datetime


def to_datetime(datetime_str: str) -> datetime:
    datetime_format = "%Y-%m-%d %H:%M:%S"
    assert isinstance(datetime_str, str), f'Expected an datetime format string for {datetime_format}'
    return datetime.strptime(datetime_str, datetime_format)
