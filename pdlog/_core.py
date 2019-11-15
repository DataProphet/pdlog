import logging
from functools import wraps

import pandas as pd

from ._utils import percent


logger = logging.getLogger("pdlog")


@pd.api.extensions.register_dataframe_accessor("log")
class FrameLogMethods:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    def __call__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @wraps(pd.DataFrame.dropna)
    def dropna(self, *args, **kwargs):
        new_data = self._data.dropna(*args, **kwargs)
        log_filter(self._data, new_data, "dropna")
        return new_data


def log_filter(before_df: pd.DataFrame, after_df: pd.DataFrame, function: str) -> None:
    """Log changes in a dataframe for filtering operations (drop rows/cols)."""

    n_rows_before = len(before_df)
    n_rows_after = len(after_df)
    n_rows_dropped = n_rows_before - n_rows_after

    cols_dropped = sorted(set(after_df.columns) - set(before_df.columns))
    n_cols_before = before_df.shape[1]
    n_cols_dropped = len(cols_dropped)

    if n_rows_before < n_rows_after:
        raise ValueError(f"function: {function} added rows, it is not a filter operation")
    elif n_rows_before == 0:
        logger.info("%s: empty input dataframe", function)
    elif n_rows_after == 0:
        logger.critical("%s: dropped all rows", function)
    elif n_cols_dropped > 0:
        logger.info(
            "%s: dropped %d columns (%s): %s",
            function,
            n_cols_dropped,
            percent(n_cols_dropped, n_cols_before),
            cols_dropped
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
