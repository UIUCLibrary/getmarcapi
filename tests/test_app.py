from unittest.mock import Mock

from getmarcapi.app import get_cli_parser, main
import pytest


def test_get_cli_check_parser():
    parser = get_cli_parser()
    args = parser.parse_args(["--check"])
    assert args.check is True


@pytest.mark.parametrize("is_valid,expected_exit_code", [(True, 0), (False, 1)])
def test_checks_arg_exits(is_valid, expected_exit_code, monkeypatch):
    args = Mock(check=True)
    checker = Mock(return_value=is_valid)
    with pytest.raises(SystemExit) as e:
        main(args, checker)
    assert e.value.code == expected_exit_code
