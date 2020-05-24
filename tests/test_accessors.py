import logging
import pandas as pd
import pytest
from numpy import nan
from pandas.testing import assert_frame_equal

import pdlog  # noqa


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture(scope="session")
def titanic():
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
    return pd.read_csv(url)


def _test_log_accessor_method(
    caplog, df, method, kwargs, expected_level, expected_message
):
    result = getattr(df.log, method)(**kwargs)
    expected = getattr(df, method)(**kwargs)
    assert_frame_equal(result, expected)
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == expected_level
    assert record.message == expected_message


@pytest.mark.parametrize(
    ("method", "kwargs", "expected_level", "expected_message"),
    (
        pytest.param(
            "dropna",
            {},
            logging.INFO,
            "dropna: dropped 709 rows (80%), 182 rows remaining",
            id="dropna",
        ),
        pytest.param(
            "drop_duplicates",
            {},
            logging.INFO,
            "drop_duplicates: dropped 107 rows (12%), 784 rows remaining",
            id="drop_duplicates",
        ),
        pytest.param(
            "query",
            {"expr": "age < 24 and alive"},
            logging.INFO,
            "query: dropped 644 rows (72%), 247 rows remaining",
            id="query",
        ),
        pytest.param(
            "head",
            {},
            logging.INFO,
            "head: dropped 886 rows (>99%), 5 rows remaining",
            id="head",
        ),
        pytest.param(
            "tail",
            {},
            logging.INFO,
            "tail: dropped 886 rows (>99%), 5 rows remaining",
            id="tail",
        ),
        pytest.param(
            "sample",
            {"frac": 0.1, "random_state": 42},
            logging.INFO,
            "sample: dropped 802 rows (90%), 89 rows remaining",
            id="sample",
        ),
        pytest.param(
            "drop",
            {"index": [0, 1, 42]},
            logging.INFO,
            "drop: dropped 3 rows (<1%), 888 rows remaining",
            id="drop_index",
        ),
        pytest.param(
            "drop",
            {"columns": ["survived", "deck", "alone"]},
            logging.INFO,
            "drop: dropped 3 columns (20%): ['alone', 'deck', 'survived']",
            id="drop_columnns",
        ),
        pytest.param(
            "set_index",
            {"keys": ["survived"]},
            logging.INFO,
            (
                "set_index: set from 'None' (RangeIndex): [0, ..., 890] "
                "to 'survived' (Int64Index): [0, ..., 0]"
            ),
            id="set_index",
        ),
        pytest.param(
            "reset_index",
            {},
            logging.INFO,
            (
                "reset_index: set from 'None' (RangeIndex): [0, ..., 890] "
                "to 'None' (RangeIndex): [0, ..., 890]"
            ),
            id="reset_index",
        ),
        pytest.param(
            "rename",
            {"columns": {"alone": "not_together", "survived": "not_dead"}},
            logging.INFO,
            "rename: renamed 2 columns: ['not_dead', 'not_together']",
            id="rename_columns",
        ),
        pytest.param(
            "fillna",
            {"value": 0},
            logging.INFO,
            "fillna: filled 869 observations (7.0%)",
            id="fillna",
        ),
        pytest.param(
            "ffill",
            {},
            logging.INFO,
            "ffill: filled 868 observations (6.0%)",
            id="ffill",
        ),
        pytest.param(
            "bfill",
            {},
            logging.INFO,
            "bfill: filled 868 observations (6.0%)",
            id="bfill",
        ),
    ),
)
def test_log_accessor(
    caplog, titanic, method, kwargs, expected_level, expected_message
):
    _test_log_accessor_method(
        caplog, titanic, method, kwargs, expected_level, expected_message
    )


def test_log_accessor_pivot(caplog):
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-01-02"],
            "feature": ["foo", "bar", "foo"],
            "value": [0, 1, 2],
        }
    )
    _test_log_accessor_method(
        caplog=caplog,
        df=df,
        method="pivot",
        kwargs={"index": "date", "columns": "feature", "values": "value"},
        expected_level=logging.INFO,
        expected_message=(
            "pivot: reshaped from (3, 3) to (2, 2). "
            "old columns: ['date', 'feature', 'value']. "
            "new columns: ['bar', 'foo']"
        ),
    )


def test_log_accessor_melt(caplog):
    df = pd.DataFrame(
        {"date": ["2020-01-01", "2020-01-02"], "bar": [1, nan], "foo": [0, 2]}
    )
    _test_log_accessor_method(
        caplog=caplog,
        df=df,
        method="melt",
        kwargs={"id_vars": "date"},
        expected_level=logging.INFO,
        expected_message=(
            "melt: reshaped from (2, 3) to (4, 3). "
            "old columns: ['date', 'bar', 'foo']. "
            "new columns: ['date', 'variable', 'value']"
        ),
    )
