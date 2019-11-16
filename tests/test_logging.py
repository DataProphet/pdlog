import logging

import numpy as np
import pandas as pd
import pytest

from pdlog.logging import log_filter


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


def test_filter_rows_none(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame([0, 1, 2])
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped no rows")
    ]


def test_filter_rows_all(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame()
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.CRITICAL, "test_filter: dropped all rows")
    ]


def test_filter_rows_some(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame([0, 1])
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped 1 rows (33%), 2 rows remaining")
    ]


def test_filter_rows_less_1pct(caplog):
    before_df = pd.DataFrame(np.arange(101))
    after_df = pd.DataFrame(np.arange(100))
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped 1 rows (<1%), 100 rows remaining")
    ]


def test_filter_rows_greater_99pct(caplog):
    before_df = pd.DataFrame(np.arange(101))
    after_df = pd.DataFrame([0])
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        (
            "pdlog",
            logging.INFO,
            "test_filter: dropped 100 rows (>99%), 1 rows remaining",
        )
    ]


def test_filter_empty_df(caplog):
    before_df = pd.DataFrame()
    after_df = pd.DataFrame()
    log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: empty input dataframe")
    ]


def test_filter_rows_added(caplog):
    before_df = pd.DataFrame()
    after_df = pd.DataFrame([0, 1, 2])
    with pytest.raises(
        ValueError,
        match="function: test_filter added rows, it is not a filter operation",
    ):
        log_filter(before_df, after_df, "test_filter")
