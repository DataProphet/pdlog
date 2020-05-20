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


def summarize(items: Sequence, max_items: int = 3) -> str:
    if len(items) > max_items:
        items = [items[0], ..., items[-1]]
    item_strings = (_stringify(x) for x in items)
    result = ", ".join(item_strings)
    return f"[{result}]"


ELLIPSIS_TYPE = type(Ellipsis)


def _stringify(item: Any) -> str:
    if isinstance(item, str):
        return f"'{item}'"
    if isinstance(item, ELLIPSIS_TYPE):
        return "..."
    return str(item)
