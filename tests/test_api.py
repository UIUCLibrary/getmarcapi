import flask
import pytest
import getmarcapi
import uiucprescon.getmarc2.records
import xml.etree.ElementTree as ET


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
    rc = client.get('/api/record?bib_id=12345')
    assert rc.status_code == 200
    assert rc.content_type == 'text/xml'


def test_get_record_missing_param(client):
    rc = client.get('/api/record')
    assert rc.status_code == 422


def test_api_documentation(client):
    rc = client.get('/api')
    assert rc.status_code == 200


def pytest_generate_tests(metafunc):
    app = getmarcapi.app
    if "route" in metafunc.fixturenames:
        app.config['testing'] = True
        app.config['API_DOMAIN'] = "testing"
        app.config['API_KEY'] = "NA"
        routes_to_skip = ['/api/record']
        with app.test_client() as client:
            rc = client.get('/api')
            metafunc.parametrize(
                "route",
                filter(lambda x: x not in routes_to_skip,
                       map(lambda x: x['route'], rc.json)
                       )
            )

        del app.config['API_DOMAIN']
        del app.config['API_KEY']


def test_api_documentation_valid_endpoints(route, client):
    rc = client.get(route)
    assert rc.status_code == 200


def test_api_955_option_with(monkeypatch, client):
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

    monkeypatch.setattr(uiucprescon.getmarc2.records.RecordServer, "get_record",
                        mock_get_record_response)
    rc = client.get('/api/record?bib_id=12345&enhance=955&enhance=333')
    assert rc.status_code == 200
    d = ET.fromstring(rc.data)
    fields = d.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='955']")
    assert len(fields) == 1


def test_api_955_option_without(monkeypatch, client):
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

    monkeypatch.setattr(uiucprescon.getmarc2.records.RecordServer, "get_record",
                        mock_get_record_response)
    rc = client.get('/api/record?bib_id=12345')
    assert rc.status_code == 200
    d = ET.fromstring(rc.data)
    fields = d.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='955']")
    assert len(fields) == 0
