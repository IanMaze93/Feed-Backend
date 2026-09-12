import pytest

from src.tools.normalize.normalize_string import normalize_string, normalize_url


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Artificial Intelligence  ", "artificial intelligence"),
        ("Mixed CASE", "mixed case"),
        ("", ""),
    ],
)
def test_normalize_string(value, expected):
    assert normalize_string(value) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            " HTTPS://Example.COM/News.RSS/ ",
            "https://example.com/news",
        ),
        (
            "https://example.com/feed/?topic=Python#latest",
            "https://example.com/feed?topic=Python",
        ),
        (
            "https://example.com/Feed/",
            "https://example.com/feed",
        ),
    ],
)
def test_normalize_url_removes_fragments_and_normalizes_url_parts(url, expected):
    assert normalize_url(url) == expected
