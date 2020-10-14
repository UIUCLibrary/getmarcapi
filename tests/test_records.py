from getmarcapi import records
import pytest


def test_invalid_record_strategy():
    invalid_args = {
        "dummy": "bad"
    }
    with pytest.raises(ValueError):
        strat = records.RecordGetter(args=invalid_args)


def test_bibid_record_strategy():
    request_args = {
        "bibid": "sample"
    }
    strat = records.RecordGetter(args=request_args)
    assert "Bibid" in str(strat)

