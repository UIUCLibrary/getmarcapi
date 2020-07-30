from unittest.mock import Mock

from getmarcapi.app import get_cli_parser, main
import pytest

def test_get_cli_check_parser():
    parser = get_cli_parser()
    args = parser.parse_args(["--check"])
    assert args.check is True


def test_checks_exits(monkeypatch):
    args = Mock(check=True)
    with pytest.raises(SystemExit):
        main(args)
