import re


def parse_int(source: str) -> int:
    if source is None:
        return None

    assert isinstance(source, str), "Expected digit string"
    match = re.search(r'\b\d+\b', source)
    return int(match.group(0))
