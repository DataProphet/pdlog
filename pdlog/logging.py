# NOTE: Have taken care to not keep copies in memory, hence we overwrite original df.
# TODO: Summarize more things
# TODO: Could we refactor something out here?
#       E.g., having to log every time by passing in the function and elapsed time seems
#       like an abstraction is waiting...
# TODO: Should elapsed be DEBUG or INFO?
from datetime import timedelta
import logging
from typing_extensions import Protocol

import pandas as pd

from .utils import percent, summarize


logger = logging.getLogger("pdlog")


class LogFunction(Protocol):
    def __call__(
        self, df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
    ) -> pd.DataFrame:
        ...


def _apply_df_function(
    df: pd.DataFrame, function_name: str, *args, **kwargs
) -> pd.DataFrame:
    function = getattr(df, function_name)
    return function(*args, **kwargs)


def log_filter(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:
    """Log changes in a dataframe for filter operations (dropped rows/cols)."""

    n_rows_before = len(df)
    n_cols_before = df.shape[1]
    before_columns = df.columns

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    n_rows_after = len(df)
    n_rows_dropped = n_rows_before - n_rows_after

    n_cols_after = df.shape[1]
    n_cols_dropped = n_cols_before - n_cols_after

    # TODO: Can this be cleaned up?
    if n_rows_before < n_rows_after:
        raise ValueError(
            f"function: {function_name} added rows, it is not a valid filter operation"
        )
    elif n_cols_before < n_cols_after:
        raise ValueError(
            f"function: {function_name} added columns, it is not a valid filter operation"
        )
    elif n_rows_before == 0:
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
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df


def log_assign(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:
    """Log changes in a dataframe for assignment operations (added cols)."""

    before_columns = df.columns

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    # new_columns = [c for c in after_df.columns if c not in before_df.columns]
    new_columns = df.columns.difference(before_columns).tolist()

    if new_columns:
        logger.info(
            "%s: added %d columns: %s", function_name, len(new_columns), new_columns
        )

    # TODO: Cleanup
    function_kwargs = {
        k: v.__name__ if callable(v) else v for k, v in function_kwargs.items()
    }
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df


def log_change_index(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:

    before_index_name = df.index.name
    before_index_type = type(df.index).__name__

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    after_index_name = df.index.name
    after_index_type = type(df.index).__name__

    # HACK
    elapsed = timedelta(hours=1)

    # TODO: Could show first and last vals, not sure if important...
    logger.info(
        "%s – %ss: set from '%s' (%s) to '%s' (%s)",
        function_name,
        elapsed.total_seconds(),
        before_index_name,
        before_index_type,
        after_index_name,
        after_index_type,
    )
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df


def log_rename(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:

    before_index = df.index
    before_columns = df.columns

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    new_columns = df.columns.difference(before_columns).tolist()
    if new_columns:
        logger.info(
            "%s: renamed %d columns: %s",
            function_name,
            len(new_columns),
            summarize(new_columns),
        )
    else:
        new_rows = df.index.difference(before_index).tolist()
        if new_rows:
            logger.info(
                "%s: renamed %d rows: %s",
                function_name,
                len(new_rows),
                summarize(new_rows),
            )

    # TODO: Refactor to a util function log func args?
    # TODO: util function should also summarize kwargs?
    function_kwargs = {
        k: v.__name__ if callable(v) else v for k, v in function_kwargs.items()
    }
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df


def log_reindex(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:
    pass


def log_reshape(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:

    before_shape = df.shape
    before_columns = df.columns

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    logger.info(
        "%s: reshaped from %s %s to %s %s",
        function_name,
        before_shape,
        summarize(before_columns, max_items=5),
        df.shape,
        summarize(df.columns, max_items=5),
    )
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df


# TODO: This one requires the grouping function object...
# def log_groupby(
#     df: pd.DataFrame,
#     function_name: str,
#     *function_args,
#     **function_kwargs,
# ) -> pd.DataFrame:

#     function = getattr(df, function_name)

#     import pdb; pdb.set_trace()

#     before_df = df
#     after_df = function(*function_args, **function_kwargs)

#     logger.info("%s: reshaped from %s %s to %s %s",
#                 function, before_df.shape, summarize(before_df.columns, max_items=5),
#                 after_df.shape, summarize(after_df.columns, max_items=5))
#     logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)


def log_fillna(
    df: pd.DataFrame, function_name: str, *function_args, **function_kwargs
) -> pd.DataFrame:

    n_obs = df.shape[0] * df.shape[1]
    before_nan_mask = df.isna()

    df = _apply_df_function(df, function_name, *function_args, **function_kwargs)

    after_nan_mask = df.isna()

    filled_nan_mask = (~after_nan_mask) & before_nan_mask
    n_filled_nans = filled_nan_mask.sum().sum()

    logger.info(
        "%s: filled %d/%d (%s) observations",
        function_name,
        n_filled_nans,
        n_obs,
        percent(n_filled_nans, n_obs),
    )
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)

    return df
