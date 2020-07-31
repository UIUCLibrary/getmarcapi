from unittest.mock import Mock

import getmarcapi.config
import getmarcapi


def test_config_file(tmpdir):
    config_file = tmpdir.join("sample.cfg")
    sample_config_data = '''[ALMA_API]
API_DOMAIN = http://www.fake.com
api_key = fake12345
    '''
    config_file.write(sample_config_data)
    config_strategy = getmarcapi.config.ConfigFile(config_file.strpath)
    domain = config_strategy.get_config_value('API_DOMAIN')
    assert domain == "http://www.fake.com"


def test_config_env(monkeypatch):

    monkeypatch.setenv('ALMA_API_DOMAIN', 'http://www.fake.com')
    config_strategy = getmarcapi.config.EnvConfig()
    domain = config_strategy.get_config_value('API_DOMAIN')
    assert domain == "http://www.fake.com"


def test_empty_config_loader():
    app = getmarcapi.app
    getmarcapi.config.get_config(app)

    assert app.config['API_DOMAIN'] is None
    assert app.config['API_KEY'] is None


def test_mixed_config_loader(monkeypatch, tmpdir):

    monkeypatch.setenv('ALMA_API_DOMAIN', 'http://www.fake.com')
    config_file = tmpdir.join("sample.cfg")
    sample_config_data = '''[ALMA_API]
    API_KEY = spam
    '''
    config_file.write(sample_config_data)
    monkeypatch.setenv('GETMARCAPI_SETTINGS', config_file.strpath)

    app = getmarcapi.app
    getmarcapi.config.get_config(app)

    assert app.config['API_DOMAIN'] == 'http://www.fake.com'
    assert app.config['API_KEY'] == "spam"


def test_mixed_overwrite_config_loader(monkeypatch, tmpdir):
    app = getmarcapi.app
    del app.config['API_DOMAIN']
    del app.config['API_KEY']

    monkeypatch.setenv('ALMA_API_DOMAIN', 'http://www.python.com')
    config_file = tmpdir.join("sample.cfg")
    sample_config_data = '''[ALMA_API]
    API_DOMAIN = "http://www.wrong_one.com"
    API_KEY = spam
    '''
    config_file.write(sample_config_data)
    monkeypatch.setenv('GETMARCAPI_SETTINGS', config_file.strpath)

    getmarcapi.config.get_config(app)

    assert app.config['API_DOMAIN'] == 'http://www.python.com'
    assert app.config['API_KEY'] == "spam"


def test_check_empty_config():
    app = getmarcapi.app
    if "API_DOMAIN" in app.config:
        del app.config['API_DOMAIN']

    if 'API_KEY' in app.config:
        del app.config['API_KEY']

    assert getmarcapi.config.check_config(app) is False


def test_check_env_config():
    app = getmarcapi.app
    app.config['API_DOMAIN'] = "http://www.fake.com"
    app.config['API_KEY'] = "1234"

    assert getmarcapi.config.check_config(app) is True


def test_check_missing_api_key_config():
    app = getmarcapi.app
    app.config['API_DOMAIN'] = "http://www.fake.com"
    if 'API_KEY' in app.config:
        del app.config['API_KEY']

    assert getmarcapi.config.check_config(app) is True


def test_warn_getmarcapi_settings_not_valid(monkeypatch):
    app = getmarcapi.app
    monkeypatch.setenv('GETMARCAPI_SETTINGS', 'not_a_valid_file.cfg')
    app.logger.warning = Mock()
    getmarcapi.config.get_config(app)
    app.logger.warning.assert_called()
