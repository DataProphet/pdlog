from datetime import datetime
from functools import wraps
from typing import Callable

import pandas as pd

from . import logging


@pd.api.extensions.register_dataframe_accessor("log")
class FrameLogMethods:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @staticmethod
    def add_hooks(
        method_name: str,
        after_hook: Callable[[pd.DataFrame, pd.DataFrame, str], None] = None,
    ):
        """
        Return an accessor method that calls self._data.method_name with hooks.

        Used to patch the underlying pd.DataFrame methods with added logging.
        """

        @wraps(getattr(pd.DataFrame, method_name))
        def inner(self, *args, **kwargs):

            before_time = datetime.now()

            df_method = getattr(self._data, method_name)

            after_df = df_method(*args, **kwargs)

            after_time = datetime.now()
            elapsed = after_time - before_time

            if after_hook is not None:
                after_hook(self._data, after_df, method_name, args, kwargs, elapsed)

            return after_df

        return inner


# TODO: Add tests
# TODO: Use decorators instead?
# TODO: getitem and setitem seem like a bit of a nightmare... Maybe just don't support it?
LOGGED_METHODS = {
    "dropna": {"after_hook": logging.log_filter},
    "drop_duplicates": {"after_hook": logging.log_filter},
    "iloc": {"after_hook": logging.log_filter},
    "loc": {"after_hook": logging.log_filter},
    "__getitem__": {"after_hook": logging.log_filter},
    "query": {"after_hook": logging.log_filter},
    "assign": {"after_hook": logging.log_assign},
    "set_index": {"after_hook": logging.log_set_index},
    "reset_index": {"after_hook": logging.log_set_index},
}
for method_name, kwargs in LOGGED_METHODS.items():
    setattr(
        FrameLogMethods, method_name, FrameLogMethods.add_hooks(method_name, **kwargs)
    )
