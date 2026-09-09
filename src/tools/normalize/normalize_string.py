from urllib.parse import urlsplit, urlunsplit


def normalize_string(input_string: str) -> str:
    """
    Normalize a string by converting it to lowercase and stripping
    leading/trailing whitespace.

    Args:
        input_string (str): The string to normalize.

    Returns:
        str: The normalized string.
    """
    return input_string.lower().strip()


def normalize_url(url: str) -> str:
    url = url.strip()

    parts = urlsplit(url)

    path = parts.path.rstrip("/").lower()

    if path.endswith(".rss"):
        path = path[:-4]

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            parts.query,
            "",
        )
    )
