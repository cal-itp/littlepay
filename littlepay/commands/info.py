from littlepay import __version__ as version
from littlepay.commands import RESULT_SUCCESS, RESULT_FAILURE


def info() -> int:
    """Print information about this package and the environment.

    Returns:
        A value indicating if the operation succeeded or failed.
    """
    res = RESULT_SUCCESS

    print(f"littlepay: {version}")

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
