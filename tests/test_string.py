import pytest

from pdlog.string import percent
from pdlog.string import plural
from pdlog.string import summarize


@pytest.mark.parametrize(
    ("n", "noun", "expected"),
    (
        pytest.param(0, "row", "0 rows", id="zero"),
        pytest.param(1, "row", "1 row", id="one"),
        pytest.param(42, "row", "42 rows", id=">1"),
    ),
)
def test_plural(n, noun, expected):
    assert plural(n, noun) == expected


@pytest.mark.parametrize(
    ("n", "total", "expected"),
    (
        pytest.param(0, 1234, "0%", id="0%"),
        pytest.param(1234, 1234, "100%", id="100%"),
        pytest.param(1, 1234, "<1%", id="<1%__0"),
        pytest.param(1, 101, "<1%", id="<1%__1"),
        pytest.param(1233, 1234, ">99%", id=">99%__0"),
        pytest.param(100, 101, ">99%", id=">99%__1"),
        pytest.param(42, 100, "42%", id="default"),
    ),
)
def test_percent(n, total, expected):
    assert percent(n, total) == expected


@pytest.mark.parametrize(
    ("items", "expected"),
    (
        pytest.param([1, 2, 3], "[1, 2, 3]", id="show_all"),
        pytest.param(["1", "2", "3"], "['1', '2', '3']", id="show_all_with_strings"),
        pytest.param([1, 2, 3, 4], "[1, ..., 4]", id="summarize"),
        pytest.param(
            ["1", "2", "3", "4"], "['1', ..., '4']", id="summarize_with_strings"
        ),
    ),
)
def test_summarize(items, expected):
    assert summarize(items, max_items=3) == expected
