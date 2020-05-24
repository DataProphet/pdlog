import logging
from unittest.mock import Mock

import pandas as pd
import pytest
from numpy import nan

from pdlog.logging import log_change_index
from pdlog.logging import log_fillna
from pdlog.logging import log_filter
from pdlog.logging import log_rename
from pdlog.logging import log_reshape


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


def _test_log_function(
    log_fn, caplog, before_df, after_df, expected_level, expected_msg
):
    fn_args = Mock()
    fn_kwargs = Mock()
    before_df.fn = Mock(return_value=after_df)

    log_fn(before_df, "fn", fn_args, fn_kwargs)

    before_df.fn.assert_called_once_with(fn_args, fn_kwargs)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == expected_level
    assert record.message == expected_msg


@pytest.mark.parametrize(
    ("before", "after", "expected_level", "expected_msg"),
    (
        pytest.param([], [], logging.INFO, "fn: empty input dataframe", id="empty_df"),
        pytest.param(
            [0, 1, 2], [], logging.CRITICAL, "fn: dropped all rows", id="all_rows"
        ),
        pytest.param(
            {"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]},
            {"x": [1]},
            logging.INFO,
            "fn: dropped 2 columns (67%) and 2 rows (67%), 1 row remaining",
            id="some_rows_and_cols",
        ),
        pytest.param(
            [0, 1, 2],
            [0, 1],
            logging.INFO,
            "fn: dropped 1 row (33%), 2 rows remaining",
            id="some_rows",
        ),
        pytest.param(
            {"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]},
            {"x": [1, 2, 3]},
            logging.INFO,
            "fn: dropped 2 columns (67%): ['y', 'z']",
            id="some_cols",
        ),
        pytest.param(
            [0, 1, 2], [0, 1, 2], logging.INFO, "fn: dropped no rows", id="no_rows"
        ),
    ),
)
def test_log_filter(caplog, before, after, expected_level, expected_msg):
    before_df = pd.DataFrame(before)
    after_df = pd.DataFrame(after)
    _test_log_function(
        log_filter, caplog, before_df, after_df, expected_level, expected_msg
    )


@pytest.mark.parametrize(
    ("before", "after", "error", "error_msg"),
    [
        pytest.param(
            [],
            [0, 1, 2],
            AssertionError,
            "function: fn added rows, it is not a valid filter operation",
            id="add_rows",
        ),
        pytest.param(
            {"x": [1, 2, 3]},
            {"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]},
            AssertionError,
            "function: fn added columns, it is not a valid filter operation",
            id="add_cols",
        ),
    ],
)
def test_log_filter_raises(before, after, error, error_msg):
    before_df = pd.DataFrame(before)
    after_df = pd.DataFrame(after)
    before_df.fn = Mock(return_value=after_df)
    with pytest.raises(error, match=error_msg):
        log_filter(before_df, "fn")


@pytest.mark.parametrize(
    ("before", "after", "expected_level", "expected_msg"),
    (
        (
            pd.RangeIndex(3),
            pd.date_range("2020-01-01", "2020-01-03", name="date"),
            logging.INFO,
            (
                "fn: set from 'None' (RangeIndex): [0, 1, 2] to 'date' "
                "(DatetimeIndex): ['2020-01-01 00:00:00', "
                "'2020-01-02 00:00:00', '2020-01-03 00:00:00']"
            ),
        ),
    ),
)
def test_log_change_index(caplog, before, after, expected_level, expected_msg):
    before_df = pd.DataFrame(index=before)
    after_df = pd.DataFrame(index=after)
    _test_log_function(
        log_change_index, caplog, before_df, after_df, expected_level, expected_msg
    )


@pytest.mark.parametrize(
    (
        "before_index",
        "before_columns",
        "after_index",
        "after_columns",
        "expected_level",
        "expected_msg",
    ),
    (
        pytest.param(
            ["foo", "bar", "baz"],
            ["foo", "bar", "baz"],
            ["foo_1", "bar", "baz"],
            ["foo", "bar_1", "baz_1"],
            logging.INFO,
            (
                "fn: renamed 1 row and 2 columns. "
                "rows: ['foo_1']. columns: ['bar_1', 'baz_1']"
            ),
            id="rows_and_columns",
        ),
        pytest.param(
            ["foo", "bar", "baz"],
            [],
            ["foo", "bar_1", "baz_1"],
            [],
            logging.INFO,
            "fn: renamed 2 rows: ['bar_1', 'baz_1']",
            id="rows",
        ),
        pytest.param(
            [],
            ["foo", "bar", "baz"],
            [],
            ["foo", "bar_1", "baz_1"],
            logging.INFO,
            "fn: renamed 2 columns: ['bar_1', 'baz_1']",
            id="columns",
        ),
        pytest.param(
            ["foo", "bar", "baz"],
            ["foo", "bar", "baz"],
            ["foo", "bar", "baz"],
            ["foo", "bar", "baz"],
            logging.INFO,
            "fn: renamed nothing",
            id="nothing",
        ),
    ),
)
def test_log_rename(
    caplog,
    before_index,
    after_index,
    before_columns,
    after_columns,
    expected_level,
    expected_msg,
):
    before_df = pd.DataFrame(index=before_index, columns=before_columns)
    after_df = pd.DataFrame(index=after_index, columns=after_columns)
    _test_log_function(
        log_rename, caplog, before_df, after_df, expected_level, expected_msg
    )


@pytest.mark.parametrize(
    ("before_df", "after_df", "expected_level", "expected_msg"),
    (
        (
            pd.DataFrame(
                {
                    "timestamp": ["2019", "2019", "2020"],
                    "feature": ["a", "b", "a"],
                    "value": [0, 1, 2],
                }
            ),
            pd.DataFrame({"a": [0, 2], "b": [1, nan]}, index=["2019", "2020"]),
            logging.INFO,
            (
                "fn: reshaped from (3, 3) to (2, 2). "
                "old columns: ['timestamp', 'feature', 'value']. "
                "new columns: ['a', 'b']"
            ),
        ),
    ),
)
def test_log_reshape(caplog, before_df, after_df, expected_level, expected_msg):
    _test_log_function(
        log_reshape, caplog, before_df, after_df, expected_level, expected_msg
    )


@pytest.mark.parametrize(
    ("before", "after", "expected_level", "expected_msg"),
    (([0, 1, nan], [0, 1, 1], logging.INFO, "fn: filled 1 observation (33.0%)"),),
)
def test_log_fillna(caplog, before, after, expected_level, expected_msg):
    before_df = pd.DataFrame(before)
    after_df = pd.DataFrame(after)
    _test_log_function(
        log_fillna, caplog, before_df, after_df, expected_level, expected_msg
    )
