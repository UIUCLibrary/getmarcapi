import getmarcapi.config


def test_config_file(tmpdir):
    config_file = tmpdir.join("sample.cfg")
    sample_config_data = '''[ALMA_API]
domain = http://www.fake.com
api_key = fake12345
    '''
    config_file.write(sample_config_data)
    config_strategy = getmarcapi.config.ConfigFile(config_file.strpath)
    domain = config_strategy.get_key('domain')
    assert domain == "http://www.fake.com"


def test_config_env(monkeypatch):

    monkeypatch.setenv('ALMA_DOMAIN', 'http://www.fake.com')
    config_strategy = getmarcapi.config.EnvConfig()
    domain = config_strategy.get_key('domain')
    assert domain == "http://www.fake.com"