from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("calitp-littlepay")
except PackageNotFoundError:
    # package is not installed
    pass
