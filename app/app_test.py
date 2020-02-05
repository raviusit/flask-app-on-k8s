import pytest
from app import APP as custom_app, VERSION


@pytest.fixture
def app():
    return custom_app


@pytest.mark.unittest
def test_math_is_valud(client):
    """ Tests that it is possible to do math """
    assert (1 + 1) == 2


@pytest.mark.unittest
def test_redirect(client):
    """ Tests that the main url is redirecting to /get """
    res = client.get('/')
    assert res.status_code == 302


@pytest.mark.unittest
def test_version(client):
    """ Tests the version is correct"""
    res = client.get('/version')
    assert res.status_code == 200
    assert res.json["version"] == VERSION


@pytest.mark.integration
def test_health(client):
    """ Tests that Redis is accessible"""
    res = client.get('/healthz')
    assert res.status_code == 200
    assert res.json["ping"]

    res = client.get('/readyz')
    assert res.status_code == 200
    assert res.json["ping"]


@pytest.mark.integration
def test_integration(client):
    """ Tests that the write/get is correct"""

    # Reset the timer
    res = client.get('/reset')
    assert res.status_code == 200

    # First get should be empty
    res = client.get('/get')
    assert res.status_code == 200
    assert res.json["time"] == "None"

    # Now set the time
    res = client.get('/set')
    assert res.status_code == 200
    assert res.json["time"] != "None"
    gotTime = res.json["time"]

    # Second get should contain the previous time
    res = client.get('/get')
    assert res.status_code == 200
    assert res.json["time"] == gotTime

    # Test reset
    res = client.get('/reset')
    assert res.status_code == 200
    assert res.json["time"] == "None"

    # last get should be empty
    res = client.get('/get')
    assert res.status_code == 200
    assert res.json["time"] == "None"
