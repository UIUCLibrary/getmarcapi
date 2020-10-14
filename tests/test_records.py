from getmarcapi import records
import pytest


def test_invalid_record_strategy():
    invalid_args = {
        "dummy": "bad"
    }
    with pytest.raises(ValueError):
        strat = records.RecordGetter(args=invalid_args)


@pytest.fixture()
def bibid_request_args():
    return {
        "bibid": "sample"
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
        "mmsid": "sample"
    }


def test_mmsid_record_strategy(mmsid_request_args):
    strat = records.RecordGetter(args=mmsid_request_args)
    assert "Mmsid" in str(strat)


def test_mmsid_record_identifier(mmsid_request_args):
    strat = records.RecordGetter(args=mmsid_request_args)
    assert strat.get_identifier(args=mmsid_request_args) == "sample"

