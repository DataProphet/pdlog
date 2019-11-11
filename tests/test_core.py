import logging

import numpy as np
import pandas as pd
import pytest

import pdlog  # noqa


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


def test_dropna_rows_none(caplog):
    df = pd.DataFrame([0, 1, 2])
    expected_df = df.dropna()
    output_df = df.log.dropna()
    pd.testing.assert_frame_equal(output_df, expected_df)
    assert caplog.record_tuples == [("pdlog", logging.INFO, "dropna: dropped no rows")]


def test_dropna_rows_all(caplog):
    df = pd.DataFrame([np.nan, np.nan, np.nan])
    expected_df = df.dropna()
    output_df = df.log.dropna()
    pd.testing.assert_frame_equal(output_df, expected_df)
    assert caplog.record_tuples == [("pdlog", logging.CRITICAL, "dropna: dropped all rows")]


def test_dropna_rows_some(caplog):
    df = pd.DataFrame([0, np.nan, 2])
    expected_df = df.dropna()
    output_df = df.log.dropna()
    pd.testing.assert_frame_equal(output_df, expected_df)
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "dropna: dropped 1 rows (33%), 2 rows remaining")
    ]


def test_dropna_rows_less_1pct(caplog):
    df = pd.DataFrame(np.arange(101))
    df.iloc[42] = np.nan
    expected_df = df.dropna()
    output_df = df.log.dropna()
    pd.testing.assert_frame_equal(output_df, expected_df)
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "dropna: dropped 1 rows (<1%), 100 rows remaining")
    ]


def test_dropna_rows_greater_99pct(caplog):
    df = pd.DataFrame(np.arange(101))
    df.iloc[:-1] = np.nan
    expected_df = df.dropna()
    output_df = df.log.dropna()
    pd.testing.assert_frame_equal(output_df, expected_df)
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "dropna: dropped 100 rows (>99%), 1 rows remaining")
    ]
