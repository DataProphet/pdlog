import logging
from unittest import mock

import numpy as np
import pandas as pd
import pytest

import pdlog  # noqa


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


# TODO: Move filter tests to another module?
def test_filter_rows_none(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame([0, 1, 2])
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [("pdlog", logging.INFO, "test_filter: dropped no rows")]


def test_filter_rows_all(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame()
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [("pdlog", logging.CRITICAL, "test_filter: dropped all rows")]


def test_filter_rows_some(caplog):
    before_df = pd.DataFrame([0, 1, 2])
    after_df = pd.DataFrame([0, 1])
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped 1 rows (33%), 2 rows remaining")
    ]


def test_filter_rows_less_1pct(caplog):
    before_df = pd.DataFrame(np.arange(101))
    after_df = pd.DataFrame(np.arange(100))
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped 1 rows (<1%), 100 rows remaining")
    ]


def test_filter_rows_greater_99pct(caplog):
    before_df = pd.DataFrame(np.arange(101))
    after_df = pd.DataFrame([0])
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [
        ("pdlog", logging.INFO, "test_filter: dropped 100 rows (>99%), 1 rows remaining")
    ]


def test_filter_empty_df(caplog):
    before_df = pd.DataFrame()
    after_df = pd.DataFrame()
    pdlog.log_filter(before_df, after_df, "test_filter")
    assert caplog.record_tuples == [("pdlog", logging.INFO, "test_filter: empty input dataframe")]


def test_filter_rows_added(caplog):
    before_df = pd.DataFrame()
    after_df = pd.DataFrame([0, 1, 2])
    with pytest.raises(
        ValueError,
        match="function: test_filter added rows, it is not a filter operation"
    ):
        pdlog.log_filter(before_df, after_df, "test_filter")


def test_accessor_add_hooks():
    before_df = mock.Mock()
    after_df = mock.Mock()
    before_df.logged_method = mock.Mock(return_value=after_df)
    after_hook = mock.Mock()

    # Patch the accessor class' logged_method
    accessor_cls = pdlog.FrameLogMethods
    accessor_cls.logged_method = accessor_cls.add_hooks("logged_method", after_hook)

    # Instantiate an accessor and call the patched method
    accessor = pdlog.FrameLogMethods(before_df)
    args = (0, 1, 2)
    kwargs = dict(key0=0, key1=1, key2=2)
    accessor.logged_method(*args, **kwargs)

    # patched method calls the underlying logged_method with args and kwargs.
    before_df.logged_method.assert_called_with(*args, **kwargs)
    # patched method calls after_hook with before_df and the result of logged_method.
    after_hook.assert_called_with(before_df, after_df, "logged_method")
