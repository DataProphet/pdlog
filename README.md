# pdlog

`pdlog` provides logging for [`pandas`](https://pandas.pydata.org/) dataframes, to better enable you to monitor and debug your data pipelines.

For example:

```pycon
>>> import pdlog
>>> df = df.log.dropna()
2020-05-26 20:55:30,049 INFO <pdlog> dropna: dropped 1 row (17%), 5 rows remaining
```

## Example

The above assumes that the [`logging`](https://docs.python.org/3/library/logging.html) module has been configured and that data has been loaded into a `pandas` `DataFrame`. Let's walk through those steps with a simple example.

1. Configure `logging`:

   ```pycon
   >>> import logging
   >>> fmt = "{asctime} {levelname} <{name}> {message}"
   >>> logging.basicConfig(format=fmt, style="{", level=logging.INFO)
   ```

2. Load data into a `pandas.DataFrame`:

   ```pycon
   >>> import pandas as pd
   >>> df = pd.DataFrame([0, 1, 2, None, 4])
   >>> df.head()
        0
   0  0.0
   1  1.0
   2  2.0
   3  NaN
   4  4.0
   ```

3. Importing `pdlog` and call a method under the `log` accessor:

   ```pycon
   >>> import pdlog
   >>> df = df.log.dropna()
   2020-05-26 20:55:30,049 INFO <pdlog> dropna: dropped 1 row (17%), 5 rows remaining
   ```

## Supported methods

`pdlog` currently supports the following `pandas.DataFrame` methods:

- Filter rows and select columns:
  - `drop_duplicates`
  - `drop`
  - `dropna`
  - `head`
  - `query`
  - `sample`
  - `tail`
- (Re-)set indexes:
  - `reset_index`
  - `set_index`
- Rename indexes:
  - `rename`
- Reshape:
  - `melt`
  - `pivot`
- Impute:
  - `bfill`
  - `ffill`
  - `fillna`

## Related Work

### [`pandas-log`](https://github.com/eyaltrabelsi/pandas-log)

`pandas-log` is aimed at interactive usage. Its messages are friendlier and more verbose than `pdlog` aims to be.
Ideally, each `pdlog` message should be a single line of dense information to help you understand whether your production code is doing what you think it is, while not overflowing your logs.
These don't tend to make particularly friendly messages.

### [`tidylog`](https://github.com/elbersb/tidylog)

`pdlog` can be considered a port of `tidylog` (R package) to `pandas`.
Their goals align with ours, and we think they've done a great job at reaching those goals.
