import importlib

import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('APP_VERSION', 'v7')
    monkeypatch.setenv('APP_COLOR', 'green')
    import app
    importlib.reload(app)   # pick up the environment for this test
    return app.app.test_client()


def test_health_reports_version_and_color(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json() == {'status': 'ok', 'version': 'v7', 'color': 'green'}


def test_home_page_shows_release(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'v7' in r.data
