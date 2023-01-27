from unittest.mock import Mock

from getmarcapi import records
import pytest
from uiucprescon.getmarc2.records import NoRecordsFound


def test_invalid_record_strategy():
    invalid_args = {
        "dummy": "bad"
    }
    with pytest.raises(ValueError):
        strat = records.RecordGetter(args=invalid_args)


@pytest.fixture()
def bibid_request_args():
    return {
        "bib_id": "sample"
    }


def test_bibid_record_strategy(bibid_request_args):
    strat = records.RecordGetter(args=bibid_request_args)
    assert "Bibid" in str(strat)


def test_bibid_record_identifier(bibid_request_args):
    strat = records.RecordGetter(args=bibid_request_args)
    assert strat.get_identifier(args=bibid_request_args) == "sample"


@pytest.fixture()
def mmsid_request_args():
    return {
        "mms_id": "sample"
    }

def test_mmsid_record_strategy(mmsid_request_args):
    strat = records.RecordGetter(args=mmsid_request_args)
    assert "Mmsid" in str(strat)


def test_mmsid_record_identifier(mmsid_request_args):
    strat = records.RecordGetter(args=mmsid_request_args)
    assert strat.get_identifier(args=mmsid_request_args) == "sample"


def test_mmsid_error_strategy(mmsid_request_args, monkeypatch):
    getter = records.RecordGetter(args=mmsid_request_args)

    def mock_get_record(*args, **kwargs):
        raise NoRecordsFound(Mock())
    server = Mock()
    with pytest.raises(ValueError) as excep:
        monkeypatch.setattr(getter._strategy, "get_record", mock_get_record)
        getter.get_record(server, mmsid_request_args['mms_id'])
    assert 'No record found' in str(excep.value)


def test_bibid_error_strategy(bibid_request_args, monkeypatch):
    getter = records.RecordGetter(args=bibid_request_args)

    def mock_get_record(*args, **kwargs):
        raise NoRecordsFound(Mock())
    server = Mock()
    with pytest.raises(ValueError) as excep:
        monkeypatch.setattr(getter._strategy, "get_record", mock_get_record)
        getter.get_record(server, bibid_request_args['bib_id'])


def test_connection_error(bibid_request_args, monkeypatch):
    getter = records.RecordGetter(args=bibid_request_args)

    def mock_get_record(*args, **kwargs):
        raise ConnectionError(Mock())
    server = Mock()
    monkeypatch.setattr(getter._strategy, "get_record", mock_get_record)
    with pytest.raises(ConnectionError) as excep:
        getter.get_record(server, bibid_request_args['bib_id'])
    assert 'Unable retrieve record for sample' in str(excep.value)
