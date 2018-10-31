import app
import os, json
from requests.auth import _basic_auth_str
import pytest
import tempfile

TEST_DB = "test.db"
TEST_DATA = json.dumps({"url":"http://www.yahoo.com","suggested_short_name" : "yahoo"})
NO_URL_TEST_DATA = json.dumps({"suggested_short_name" : "yahoo"})
BAD_URL_TEST_DATA = json.dumps({"url":"htt//wwwyahoo.com","suggested_short_name" : "yahoo"})
TEST_REDIRECT_DATA = json.dumps({"short_name":"f"})
AUTH_USER = 'urlshortener'
AUTH_PASS = 'urlshortener' 
AUTH_PASS_BAD = 'ushortener' 

bad_headers = {
   'Authorization': _basic_auth_str(AUTH_USER, AUTH_PASS_BAD),
}

headers = {
   'Authorization': _basic_auth_str(AUTH_USER, AUTH_PASS),
}


@pytest.fixture
def client():
	app.create_database(TEST_DB)
	app.app.config['TESTING'] =True
	app.app.config['DB_NAME'] = TEST_DB
	client = app.app.test_client()
	yield client


	os.remove(TEST_DB)

def test_authentication(client):
	res = client.post('/', data=TEST_DATA, headers=bad_headers)
	assert res.status_code == 401

def test_shorten_url(client):
    res = client.post('/', data=TEST_DATA, headers=headers)
	
    assert res.status_code == 200

def test_no_url(client):
    res = client.post('/', data=NO_URL_TEST_DATA, headers=headers)
    assert res.status_code == 400

def test_valid_url(client):
    res = client.post('/', data=BAD_URL_TEST_DATA, headers=headers)
    assert res.status_code == 400

def test_redirect_url(client):
	res = client.get('/test', headers=headers)
	assert res.status_code == 302


def test_convert_to_base62():
	res = app.convert_to_base62(1234)
	assert res == "jU"
	
	



