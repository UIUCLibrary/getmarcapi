from getmarcapi.app import get_cli_parser


def test_get_cli_check_parser():
    parser = get_cli_parser()
    args = parser.parse_args(["--check"])
    assert args.check is True

