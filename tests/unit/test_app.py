import pytest
import json

def test_returns(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0
