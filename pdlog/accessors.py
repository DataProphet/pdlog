from functools import wraps

import pandas as pd

from . import logging


@pd.api.extensions.register_dataframe_accessor("log")
class FrameLogMethods:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @classmethod
    def add_logged_method(cls, method_name: str, log_fn: logging.LogFunction):
        @wraps(getattr(pd.DataFrame, method_name))
        def logged_method(self, *args, **kwargs):
            return log_fn(self._data, method_name, *args, **kwargs)

        logged_method.__name__ = method_name
        setattr(cls, method_name, logged_method)

    # @wraps(pd.DataFrame.groupby)
    # def groupby(self, *args, **kwargs):
    #     grouped


# TODO: Add tests
# TODO: Use decorators instead?
# TODO: getitem and setitem seem like a bit of a nightmare... Maybe just don't support it?
LOGGED_METHODS = {
    "dropna": logging.log_filter,
    "drop_duplicates": logging.log_filter,
    "iloc": logging.log_filter,
    "loc": logging.log_filter,
    "__getitem__": logging.log_filter,
    "query": logging.log_filter,
    "head": logging.log_filter,
    "tail": logging.log_filter,
    "sample": logging.log_filter,
    "drop": logging.log_filter,
    "assign": logging.log_assign,
    "set_index": logging.log_change_index,
    "reset_index": logging.log_change_index,
    "rename": logging.log_rename,
    "pivot": logging.log_reshape,
    "melt": logging.log_reshape,
    # "groupby": logging.log_groupby,
    "fillna": logging.log_fillna,
    "bfill": logging.log_fillna,
    "ffill": logging.log_fillna,
}
for method_name, log_fn in LOGGED_METHODS.items():
    FrameLogMethods.add_logged_method(method_name, log_fn)
