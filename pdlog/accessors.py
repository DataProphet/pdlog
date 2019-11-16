from functools import wraps

import pandas as pd

from . import logging


@pd.api.extensions.register_dataframe_accessor("log")
class FrameLogMethods:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @staticmethod
    def add_hooks(method_name: str, after_hook=None):
        """
        Return an accessor method that calls self._data.method_name with hooks.

        Used to patch the underlying pd.DataFrame methods with added logging.
        """
        df_method = None

        def inner(self, *args, **kwargs):

            df_method = getattr(self._data, method_name)

            after_df = df_method(*args, **kwargs)

            if after_hook is not None:
                after_hook(self._data, after_df, method_name)

            return after_df

        return wraps(df_method)(inner)


LOGGED_METHODS = {
    "dropna": {"after_hook": logging.log_filter},
    "drop_duplicates": {"after_hook": logging.log_filter},
}
for method_name, kwargs in LOGGED_METHODS.items():
    setattr(
        FrameLogMethods, method_name, FrameLogMethods.add_hooks(method_name, **kwargs)
    )
