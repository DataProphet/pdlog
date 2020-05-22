import logging
from typing import Any

import pandas as pd

from .string import percent
from .string import summarize


logger = logging.getLogger("pdlog")


def _call(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:
    function = getattr(df, function_name)
    return function(*args, **kwargs)


def log_filter(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:
    """Log changes in a dataframe for filter operations (dropped rows/cols)."""

    n_rows_before = len(df)
    n_cols_before = df.shape[1]
    before_columns = df.columns

    df = _call(df, function_name, *args, **kwargs)

    n_rows_after = len(df)
    n_rows_dropped = n_rows_before - n_rows_after

    n_cols_after = df.shape[1]
    n_cols_dropped = n_cols_before - n_cols_after

    if n_rows_before < n_rows_after:
        raise AssertionError(
            f"function: {function_name} added rows, it is not a valid filter operation"
        )
    if n_cols_before < n_cols_after:
        raise AssertionError(
            f"function: {function_name} added columns, "
            "it is not a valid filter operation"
        )
    if n_rows_before == 0:
        logger.info("%s: empty input dataframe", function_name)
    elif n_rows_after == 0:
        logger.critical("%s: dropped all rows", function_name)
    elif n_cols_dropped > 0:
        dropped_cols = sorted(set(before_columns) - set(df.columns))
        logger.info(
            "%s: dropped %d columns (%s): %s",
            function_name,
            n_cols_dropped,
            percent(n_cols_dropped, n_cols_before),
            dropped_cols,
        )
    elif n_rows_dropped == 0:
        logger.info("%s: dropped no rows", function_name)
    else:
        logger.info(
            "%s: dropped %d rows (%s), %d rows remaining",
            function_name,
            n_rows_dropped,
            percent(n_rows_dropped, n_rows_before),
            n_rows_after,
        )

    # TODO: Refactor
    logger.debug("args: %s, kwargs: %s", args, kwargs)

    return df


def log_change_index(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_index_name = df.index.name
    before_index_type = type(df.index).__name__

    df = _call(df, function_name, *args, **kwargs)

    after_index_name = df.index.name
    after_index_type = type(df.index).__name__

    # TODO: Could show first and last vals, not sure if important...
    logger.info(
        "%s: set from '%s' (%s) to '%s' (%s)",
        function_name,
        before_index_name,
        before_index_type,
        after_index_name,
        after_index_type,
    )
    logger.debug("args: %s, kwargs: %s", args, kwargs)

    return df


def log_rename(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_index = df.index
    before_columns = df.columns

    df = _call(df, function_name, *args, **kwargs)

    new_columns = df.columns.difference(before_columns).tolist()
    new_rows = df.index.difference(before_index).tolist()
    if new_columns and new_rows:
        logger.info(
            "%s: renamed %d rows and %d columns. rows: %s. columns: %s",
            function_name,
            len(new_rows),
            len(new_columns),
            summarize(new_rows),
            summarize(new_columns),
        )
    elif new_columns:
        logger.info(
            "%s: renamed %d columns: %s",
            function_name,
            len(new_columns),
            summarize(new_columns),
        )
    elif new_rows:
        logger.info(
            "%s: renamed %d rows: %s", function_name, len(new_rows), summarize(new_rows)
        )
    else:
        logger.info("%s: renamed nothing")

    # TODO: Refactor to a util function log func args?
    # TODO: util function should also summarize kwargs?
    kwargs = {k: v.__name__ if callable(v) else v for k, v in kwargs.items()}
    logger.debug("args: %s, kwargs: %s", args, kwargs)

    return df


def log_reshape(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    before_shape = df.shape
    before_columns = df.columns

    df = _call(df, function_name, *args, **kwargs)

    logger.info(
        "%s: reshaped from %s %s to %s %s",
        function_name,
        before_shape,
        summarize(before_columns, max_items=5),
        df.shape,
        summarize(df.columns, max_items=5),
    )
    logger.debug("args: %s, kwargs: %s", args, kwargs)

    return df


def log_fillna(
    df: pd.DataFrame, function_name: str, *args: Any, **kwargs: Any
) -> pd.DataFrame:

    n_obs = df.shape[0] * df.shape[1]
    before_na = df.isna()

    df = _call(df, function_name, *args, **kwargs)

    filled_na = df.notna() & before_na
    n_filled = filled_na.sum().sum()

    logger.info(
        "%s: filled %d/%d (%s) observations",
        function_name,
        n_filled,
        n_obs,
        percent(n_filled, n_obs),
    )
    logger.debug("args: %s, kwargs: %s", args, kwargs)

    return df
