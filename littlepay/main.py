import argparse
import sys

from littlepay import __version__ as version
from littlepay.commands.configure import configure
from littlepay.config import get_config_path


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

    config_parser = _subcmd("config", help="Get or set configuration.")
    config_parser.add_argument(
        "-c",
        "--config",
        default=get_config_path(),
        dest="config_path",
        help="Path to a readable and writeable config file to use. File will be created if it does not exist.",
    )
    config_parser.add_argument("--reset", action="store_true", default=False, help="Reset the configuration.")

    if len(argv) == 0:
        argv = ["config"]

    args = parser.parse_args(argv)

    if args.command == "config":
        return configure(args.config_path, args.reset)


if __name__ == "__main__":
    raise SystemExit(main())
