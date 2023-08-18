from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("littlepay")
except PackageNotFoundError:
    # package is not installed
    pass
