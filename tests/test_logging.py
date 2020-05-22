import logging
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from pdlog.logging import log_filter


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


def _test_log_function(caplog, before, after, expected_record_tuples):
    before_df = pd.DataFrame(before)
    after_df = pd.DataFrame(after)

    fn_args = Mock()
    fn_kwargs = Mock()
    before_df.fn = Mock(return_value=after_df)

    log_filter(before_df, "fn", fn_args, fn_kwargs)

    before_df.fn.assert_called_once_with(fn_args, fn_kwargs)

    assert caplog.record_tuples == expected_record_tuples


@pytest.mark.parametrize(
    ("before", "after", "expected_record_tuples"),
    (
        pytest.param(
            [0, 1, 2],
            [0, 1, 2],
            [("pdlog", logging.INFO, "fn: dropped no rows")],
            id="no_rows",
        ),
        pytest.param(
            [0, 1, 2],
            [],
            [("pdlog", logging.CRITICAL, "fn: dropped all rows")],
            id="all_rows",
        ),
        pytest.param(
            [0, 1, 2],
            [0, 1],
            [("pdlog", logging.INFO, "fn: dropped 1 rows (33%), 2 rows remaining")],
            id="some_rows",
        ),
        pytest.param(
            np.arange(101),
            np.arange(100),
            [("pdlog", logging.INFO, "fn: dropped 1 rows (<1%), 100 rows remaining")],
            id="less_1pct_rows",
        ),
        pytest.param(
            np.arange(101),
            [0],
            [("pdlog", logging.INFO, "fn: dropped 100 rows (>99%), 1 rows remaining")],
            id="greater_99pct_rows",
        ),
        pytest.param(
            [],
            [],
            [("pdlog", logging.INFO, "fn: empty input dataframe")],
            id="empty_df",
        ),
        pytest.param(
            {"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]},
            {"x": [1, 2, 3]},
            [("pdlog", logging.INFO, "fn: dropped 2 columns (67%): ['y', 'z']")],
            id="some_cols",
        ),
        # TODO: Add assign
        # TODO: Add reindex
        # TODO: Add reshape
        # TODO: Add fillna
    ),
)
def test_log_filter(caplog, before, after, expected_record_tuples):
    _test_log_function(caplog, before, after, expected_record_tuples)


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
