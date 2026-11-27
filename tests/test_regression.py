import pytest

from utils.math import add


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [(7, 5, 12), (0, 9, 9), (-4, 6, 2)],
)
def test_addition_regression_cases(left, right, expected):
    assert add(left, right) == expected
