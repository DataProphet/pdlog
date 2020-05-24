from datetime import date
from datetime import datetime
from typing import Any
from typing import Sequence


def plural(n: int, noun: str) -> str:
    if n == 1:
        return f"{n} {noun}"
    return f"{n} {noun}s"


def percent(n: int, total: int) -> str:
    if n == 0:
        return "0%"
    if n == total:
        return "100%"
    p = n / total * 100
    if p < 1:
        return "<1%"
    if p > 99:
        return ">99%"
    return f"{round(p)}%"


class _Ellipsis:
    def __repr__(self) -> str:
        return "..."


_ELLIPSIS = _Ellipsis()


def summarize(items: Sequence[Any], max_items: int = 3) -> str:
    if len(items) > max_items:
        items = [items[0], _ELLIPSIS, items[-1]]
    return str([prettify(x) for x in items])


def prettify(obj: Any) -> str:
    if isinstance(obj, (datetime, date)):
        # use str(datetime) instead of repr(datetime), it's more concise
        return str(obj)
    return obj
