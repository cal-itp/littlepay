import argparse
import sys

from littlepay import __version__ as version
from littlepay.commands.info import info


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="littlepay")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    subparsers = parser.add_subparsers(dest="command")

    def _subcmd(name, help) -> argparse.ArgumentParser:
        """Helper creates a new subcommand parser."""
        parser = subparsers.add_parser(name, help=help)
        return parser

    _subcmd("info", help="Print configuration and debugging information.")

    if len(argv) == 0:
        argv = ["info"]

    args = parser.parse_args(argv)

    if args.command == "info":
        return info()


if __name__ == "__main__":
    raise SystemExit(main())
