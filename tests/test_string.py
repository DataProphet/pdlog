from datetime import date
from datetime import datetime
from typing import Any
from typing import Sequence

import pytest
from pandas import Timestamp

from pdlog.string import percent
from pdlog.string import plural
from pdlog.string import prettify
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


class _FakeSequence(Sequence[Any]):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)


@pytest.mark.parametrize(
    ("items", "expected"),
    (
        pytest.param([1, 2, 3], "[1, 2, 3]", id="show_all"),
        pytest.param(["1", "2", "3"], "['1', '2', '3']", id="show_all_with_strings"),
        pytest.param([1, 2, 3, 4], "[1, ..., 4]", id="summarize"),
        pytest.param(
            ["1", "2", "3", "4"], "['1', ..., '4']", id="summarize_with_strings"
        ),
        pytest.param(
            ["1", "2", "3", "4"], "['1', ..., '4']", id="summarize_with_strings"
        ),
        # Class name is removed from summary string
        pytest.param(_FakeSequence([1, 2, 3]), "[1, 2, 3]", id="summarize_class"),
        pytest.param(
            [datetime(2020, 1, 1)], "['2020-01-01 00:00:00']", id="summarize_datetimes"
        ),
        pytest.param([date(2020, 1, 1)], "['2020-01-01']", id="summarize_dates"),
    ),
)
def test_summarize(items, expected):
    assert summarize(items, max_items=3) == expected


@pytest.mark.parametrize(
    ("obj", "expected"),
    (
        (Timestamp("2020-01-01 00:00:00"), "2020-01-01 00:00:00"),
        (Timestamp("2020-01-01", freq="D"), "2020-01-01 00:00:00"),
    ),
)
def test_prettify(obj, expected):
    assert prettify(obj) == expected
