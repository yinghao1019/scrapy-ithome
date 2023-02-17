import re
from datetime import datetime


def to_datetime(datetime_str: str) -> datetime:
    assert isinstance(datetime_str, str), f'Expected an datetime format string'
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as err:
        return datetime.strptime(datetime_str, "%Y/%m/%d %H:%M:%S")


def extract_datetime(datetime_str: str) -> str:
    datetime_re = r'\d{4}/\d{2}/\d{2} \d{1,2}:\d{2}:\d{2}'
    if datetime_str is not None:
        return re.search(datetime_re, datetime_str).group(0)
    return None


def get_year(timestamp: datetime) -> int:
    if timestamp is not None:
        return timestamp.year
