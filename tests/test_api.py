import pytest
import getmarcapi
from uiucprescon.getmarc2.records import RecordServer

@pytest.fixture
def client():
    getmarcapi.app.config['testing'] = True
    getmarcapi.app.config['domain'] = "testing"
    getmarcapi.app.config['api_key'] = "NA"
    with getmarcapi.app.test_client() as client:
        yield client


def test_root(client):
    rc = client.get('/')
    assert rc.status_code == 200


def test_get_record_xml(monkeypatch, client):
    def mock_response(self, bibid, *args, **kwargs):
        return ""
    monkeypatch.setattr(RecordServer, "bibid_record", mock_response)
    rc = client.get('/record?bibid=12345')
    assert rc.status_code == 200
    assert rc.content_type == 'text/xml'


def test_get_record_missing_param(client):
    rc = client.get('/record')
    assert rc.status_code == 422
