import logging

import pandas as pd

from .utils import percent


logger = logging.getLogger("pdlog")


def log_filter(before_df: pd.DataFrame, after_df: pd.DataFrame, function: str) -> None:
    """Log changes in a dataframe for filter operations (dropped rows/cols)."""

    n_rows_before = len(before_df)
    n_rows_after = len(after_df)
    n_rows_dropped = n_rows_before - n_rows_after

    n_cols_before = before_df.shape[1]
    n_cols_after = after_df.shape[1]
    n_cols_dropped = n_cols_before - n_cols_after

    if n_rows_before < n_rows_after:
        raise ValueError(
            f"function: {function} added rows, it is not a filter operation"
        )
    elif n_cols_before < n_cols_after:
        raise ValueError(
            f"function: {function} added columns, it is not a filter operation"
        )
    elif n_rows_before == 0:
        logger.info("%s: empty input dataframe", function)
    elif n_rows_after == 0:
        logger.critical("%s: dropped all rows", function)
    elif n_cols_dropped > 0:
        dropped_cols = sorted(set(before_df.columns) - set(after_df.columns))
        logger.info(
            "%s: dropped %d columns (%s): %s",
            function,
            n_cols_dropped,
            percent(n_cols_dropped, n_cols_before),
            dropped_cols,
        )
    elif n_rows_dropped == 0:
        logger.info("%s: dropped no rows", function)
    else:
        logger.info(
            "%s: dropped %d rows (%s), %d rows remaining",
            function,
            n_rows_dropped,
            percent(n_rows_dropped, n_rows_before),
            n_rows_after,
        )
