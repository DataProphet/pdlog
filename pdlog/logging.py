import logging
from typing import Any

import pandas as pd

from .string import percent
from .string import plural
from .string import summarize


logger = logging.getLogger("pdlog")


ROW = "row"
COLUMN = "column"
OBSERVATION = "observation"


def _callattr(obj: Any, name: str, *args: Any, **kwargs: Any) -> Any:
    return getattr(obj, name)(*args, **kwargs)


def log_filter(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:
    """
    Perform a filter operation with logging.

    Filter operations are those which drop rows and/or columns, for example,
    `pd.DataFrame.loc`.

    Although some methods, like `pd.DataFrame.set_index`, can be considered filter
    operations, `log_filter` doesn't cater to their use-case thus they have their own
    specific logging functions.
    """
    n_rows_before = df.shape[0]
    n_cols_before = df.shape[1]
    before_columns = df.columns

    df = _callattr(df, function_name, *args, **kwargs)

    n_rows_after = df.shape[0]
    n_rows_dropped = n_rows_before - n_rows_after

    n_cols_after = df.shape[1]
    n_cols_dropped = n_cols_before - n_cols_after

    if n_rows_dropped < 0:
        raise AssertionError(
            f"function: {function_name} added rows, it is not a valid filter operation"
        )
    if n_cols_dropped < 0:
        raise AssertionError(
            f"function: {function_name} added columns, "
            "it is not a valid filter operation"
        )

    dropped_rows = n_rows_dropped > 0
    dropped_cols = n_cols_dropped > 0

    if n_rows_before == 0:
        logger.info("%s: empty input dataframe", function_name)
    elif n_rows_after == 0:
        logger.critical("%s: dropped all rows", function_name)
    elif dropped_cols and dropped_rows:
        dropped_cols = before_columns.difference(df.columns).tolist()
        logger.info(
            "%s: dropped %s (%s) and %s (%s), %s remaining",
            function_name,
            plural(n_cols_dropped, COLUMN),
            percent(n_cols_dropped, n_cols_before),
            plural(n_rows_dropped, ROW),
            percent(n_rows_dropped, n_rows_before),
            plural(n_rows_after, ROW),
        )
    elif dropped_cols:
        dropped_cols = before_columns.difference(df.columns).tolist()
        logger.info(
            "%s: dropped %s (%s): %s",
            function_name,
            plural(n_cols_dropped, COLUMN),
            percent(n_cols_dropped, n_cols_before),
            dropped_cols,
        )
    elif dropped_rows:
        logger.info(
            "%s: dropped %s (%s), %s remaining",
            function_name,
            plural(n_rows_dropped, ROW),
            percent(n_rows_dropped, n_rows_before),
            plural(n_rows_after, ROW),
        )
    else:
        logger.info("%s: dropped no rows", function_name)

    return df


def log_change_index(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_index = summarize(df.index, 3)
    before_index_name = df.index.name
    before_index_type = type(df.index).__name__

    df = _callattr(df, function_name, *args, **kwargs)

    after_index = summarize(df.index, 3)
    after_index_name = df.index.name
    after_index_type = type(df.index).__name__

    logger.info(
        "%s: set from '%s' (%s): %s to '%s' (%s): %s",
        function_name,
        before_index_name,
        before_index_type,
        before_index,
        after_index_name,
        after_index_type,
        after_index,
    )

    return df


def log_rename(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_index = df.index
    before_columns = df.columns

    df = _callattr(df, function_name, *args, **kwargs)

    new_columns = df.columns.difference(before_columns).tolist()
    new_rows = df.index.difference(before_index).tolist()
    if new_columns and new_rows:
        logger.info(
            "%s: renamed %s and %s. rows: %s. columns: %s",
            function_name,
            plural(len(new_rows), ROW),
            plural(len(new_columns), COLUMN),
            summarize(new_rows),
            summarize(new_columns),
        )
    elif new_rows:
        logger.info(
            "%s: renamed %s: %s",
            function_name,
            plural(len(new_rows), ROW),
            summarize(new_rows),
        )
    elif new_columns:
        logger.info(
            "%s: renamed %s: %s",
            function_name,
            plural(len(new_columns), COLUMN),
            summarize(new_columns),
        )
    else:
        logger.info("%s: renamed nothing", function_name)

    return df


def log_reshape(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_shape = df.shape
    before_columns = df.columns

    df = _callattr(df, function_name, *args, **kwargs)

    logger.info(
        "%s: reshaped from %s to %s. old columns: %s. new columns: %s",
        function_name,
        before_shape,
        df.shape,
        summarize(before_columns, max_items=5),
        summarize(df.columns, max_items=5),
    )

    return df


def log_fillna(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    n_obs = df.shape[0] * df.shape[1]
    before_na = df.isna()

    df = _callattr(df, function_name, *args, **kwargs)

    filled_na = df.notna() & before_na
    n_filled = filled_na.sum().sum()

    logger.info(
        "%s: filled %s (%s)",
        function_name,
        plural(n_filled, OBSERVATION),
        percent(n_filled, n_obs),
    )

    return df
