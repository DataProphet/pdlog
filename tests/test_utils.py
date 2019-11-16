from pdlog.utils import percent


def test_percent_zero():
    assert percent(0, 1234) == "0%"


def test_percent_100():
    assert percent(1234, 1234) == "100%"


def test_percent_below_1():
    assert percent(1, 1234) == "<1%"
    assert percent(1, 101) == "<1%"


def test_percent_above_99():
    assert percent(1233, 1234) == ">99%"
    assert percent(100, 101) == ">99%"


def test_percent_default():
    assert percent(42, 101) == "42%"
