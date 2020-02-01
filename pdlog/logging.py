# TODO: Could we refactor something out here?
#       E.g., having to log every time by passing in the function and elapsed time seems
#       like an abstraction is waiting...
# TODO: Should elapsed be DEBUG or INFO?
import logging

import pandas as pd

from .utils import percent


logger = logging.getLogger("pdlog")


def log_filter(
    before_df: pd.DataFrame,
    after_df: pd.DataFrame,
    function: str,
    function_args,
    function_kwargs,
) -> None:
    """Log changes in a dataframe for filter operations (dropped rows/cols)."""

    n_rows_before = len(before_df)
    n_rows_after = len(after_df)
    n_rows_dropped = n_rows_before - n_rows_after

    n_cols_before = before_df.shape[1]
    n_cols_after = after_df.shape[1]
    n_cols_dropped = n_cols_before - n_cols_after

    if n_rows_before < n_rows_after:
        raise ValueError(
            f"function: {function} added rows, it is not a valid filter operation"
        )
    elif n_cols_before < n_cols_after:
        raise ValueError(
            f"function: {function} added columns, it is not a valid filter operation"
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

    # TODO: Don't print dataframe or series or numpy array args?
    #       Instead summarize?
    #       Would be a util func...
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)


def log_assign(before_df: pd.DataFrame, after_df: pd.DataFrame, function: str,
               function_args, function_kwargs) -> None:
    """Log changes in a dataframe for assignment operations (added cols)."""

    new_columns = [c for c in after_df.columns if c not in before_df.columns]

    if new_columns:
        logger.info("%s: added %d columns: %s", function, len(new_columns), new_columns)

    # TODO: Need args?
    # TODO: Is this necessary at all?
    #       Kwargs are just gonna be the added columns.
    #       And values are just gonna be lambdas...
    function_kwargs = {k: v.__name__ if callable(v) else v
                       for k, v in function_kwargs.items()}
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)


def log_set_index(before_df: pd.DataFrame, after_df: pd.DataFrame, function: str,
                  function_args, function_kwargs, elapsed) -> None:

    before_index_name = before_df.index.name
    before_index_type = type(before_df.index).__name__

    after_index_name = after_df.index.name
    after_index_type = type(after_df.index).__name__

    # TODO: Could show first and last vals, not sure if important...
    logger.info("%s – %ss: set from '%s' (%s) to '%s' (%s)",
                function, elapsed.total_seconds(), before_index_name, before_index_type, after_index_name, after_index_type)
    logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)


# def log_reset_index(before_df: pd.DataFrame, after_df: pd.DataFrame, function: str,
#                     function_args, function_kwargs) -> None:

#     logger.debug("args: %s, kwargs: %s", function_args, function_kwargs)
