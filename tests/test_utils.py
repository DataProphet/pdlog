import pytest

from pdlog.utils import percent


@pytest.mark.parametrize(
    "n,total,expected",
    [
        pytest.param(0, 1234, "0%", id="zero"),
        pytest.param(1234, 1234, "100%", id="100"),
        pytest.param(1, 1234, "<1%", id="less_1__0"),
        pytest.param(1, 101, "<1%", id="less_1__1"),
        pytest.param(1233, 1234, ">99%", id="greater_99__0"),
        pytest.param(100, 101, ">99%", id="greater_99__1"),
        pytest.param(42, 100, "42%", id="default"),
    ]
)
def test_percent(n, total, expected):
    assert percent(n, total) == expected
