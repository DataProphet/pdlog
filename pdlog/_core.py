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

        n_rows_before = len(self._data)
        n_rows_after = len(new_data)
        n_rows_dropped = n_rows_before - n_rows_after

        cols_dropped = sorted(set(new_data.columns) - set(self._data.columns))
        n_cols_before = self._data.shape[1]
        n_cols_dropped = len(cols_dropped)

        if n_rows_after == 0:
            logger.critical("dropna: dropped all rows")
        elif n_cols_dropped > 0:
            logger.info(
                "dropna: dropped %d columns (%s): %s",
                n_cols_dropped,
                percent(n_cols_dropped, n_cols_before),
                cols_dropped
            )
        elif n_rows_dropped == 0:
            logger.info("dropna: dropped no rows")
        else:
            logger.info(
                "dropna: dropped %d rows (%s), %d rows remaining",
                n_rows_dropped,
                percent(n_rows_dropped, n_rows_before),
                n_rows_after,
            )

        return new_data
