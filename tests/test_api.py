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
    def mock_get_record_response(self, identifier, identifier_type):
        mock_xml_record = """
        <record xmlns="http://www.loc.gov/MARC21/slim" 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                xsi:schemaLocation="http://www.loc.gov/MARC21/slim 
                http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
        <leader>00834cam a2200253 i 4500</leader>
        </record>
        """
        return mock_xml_record

    monkeypatch.setattr(uiucprescon.getmarc2.records.RecordServer, "get_record", mock_get_record_response)
    rc = client.get('/record?bib_id=12345')
    assert rc.status_code == 200
    assert rc.content_type == 'text/xml'


def test_get_record_missing_param(client):
    rc = client.get('/record')
    assert rc.status_code == 422
