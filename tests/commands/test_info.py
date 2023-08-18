from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.info import info


def test_info():
    res = info()

    assert res == RESULT_SUCCESS
