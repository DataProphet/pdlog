# pdlog

`pdlog` provides logging for pandas dataframes.
Its purpose is to better enable you to monitor and debug your data pipelines.

## Installation

```bash
$ pip install pdlog
```

## Example

TODO: Write out some examples...

TODO: Link to another page for a complete set of examples?

## Related Work

### [`pandas-log`](https://github.com/eyaltrabelsi/pandas-log)

`pandas-log` is more geared towards interactive usage, so its messages are friendlier and more verbose than `pdlog` aims to be.
Ideally, each `pdlog` message should be a single line of dense information to help you understand whether your production code is doing what you think it is, while not overflowing your logs.
These don't tend to make particularly friendly messages.

### [`tidylog`](https://github.com/elbersb/tidylog)

`pdlog` is very similar to `tidylog`.
Their goals seem to align with ours, and we think they've done a great job at reaching those goals.
You could consider `pdlog` a `pandas` port of `tidylog`.
