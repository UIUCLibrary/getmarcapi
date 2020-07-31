import flask
import pytest
import getmarcapi
import uiucprescon.getmarc2.records


@pytest.fixture
def client():
    app = getmarcapi.app
    app.config['testing'] = True
    app.config['API_DOMAIN'] = "testing"
    app.config['API_KEY'] = "NA"

    with app.test_client() as client:
        yield client

    del app.config['API_DOMAIN']
    del app.config['API_KEY']


def test_root(client):
    rc = client.get('/')
    assert rc.status_code == 200


def test_get_record_xml(monkeypatch, client):
    def mock_response(self, bibid, *args, **kwargs):
        return ""
    monkeypatch.setattr(uiucprescon.getmarc2.records.RecordServer, "bibid_record", mock_response)
    rc = client.get('/record?bibid=12345')
    assert rc.status_code == 200
    assert rc.content_type == 'text/xml'


def test_get_record_missing_param(client):
    rc = client.get('/record')
    assert rc.status_code == 422
