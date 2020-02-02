def plural(n: int, noun: str) -> str:
    if n == 1:
        return f"{n} {noun}"
    else:
        return f"{n} {noun}s"


def percent(n: int, total: int) -> str:
    p = n / total * 100
    if n == 0:
        return "0%"
    elif n == total:
        return "100%"
    elif p < 1:
        return "<1%"
    elif p > 99:
        return ">99%"
    else:
        return f"{round(p)}%"


def summarize(iterable, max_items=3) -> str:
    length = len(iterable)
    if length <= max_items:
        return str(list(iterable))
    else:
        first, last = iterable[0], iterable[-1]
        if isinstance(first, str):
            first = f"'{first}'"
        if isinstance(last, str):
            last = f"'{last}'"
        return f"[{first}, ..., {last}]"
