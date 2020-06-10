import pytest

def test_returns(test_client):
    response = test_client.get('/')
    assert response.data == b'No'
