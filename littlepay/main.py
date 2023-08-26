from argparse import ArgumentParser
import sys

from littlepay import __version__ as version
from littlepay.commands.configure import configure
from littlepay.commands.switch import switch
from littlepay.config import CONFIG_TYPES, Config


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = ArgumentParser(prog="littlepay")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        help="Path to a readable and writeable config file to use. File will be created if it does not exist.",
    )

    subparsers = parser.add_subparsers(dest="command")

    def _subcmd(name, help) -> ArgumentParser:
        """Helper creates a new subcommand parser."""
        parser = subparsers.add_parser(name, help=help)
        return parser

    config_parser = _subcmd("config", help="Get or set configuration.")
    config_parser.add_argument(
        "config_path",
        nargs="?",
        default=Config.current_path(),
    )

    switch_parser = _subcmd("switch", help="Switch the active environment or participant.")
    switch_parser.add_argument("switch_type", choices=CONFIG_TYPES, help="The type of object to switch", metavar="TYPE")
    switch_parser.add_argument("switch_arg", help="The new object value", metavar="VALUE")

    if len(argv) == 0:
        argv = ["config"]

    args = parser.parse_args(argv)

    if args.command == "config" or args.config_path:
        return configure(args.config_path)
    elif args.command == "switch":
        return switch(args.switch_type, args.switch_arg)


if __name__ == "__main__":
    raise SystemExit(main())
