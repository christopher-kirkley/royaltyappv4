import pytest
import json

from royaltyapp.models import Artist

def test_can_get_all_artists(test_client):
    response = test_client.get('/artists')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0

def test_can_add_artist(test_client):
    data = {'artist_name': 'Amanar',
            'prenom': 'Ahmed',
            'surnom': 'Ag Kaedi'
            }
    json_data = json.dumps(data)
    response = test_client.post('/artists', data=json_data)
    assert response.status_code == 200
    result = Artist.query.all()
    assert len(result) == 1
    assert json.loads(response.data) == {'success': 'true'}

    

    
    # response = test_client.get('/artists')
    # assert response.status_code == 200
    # assert len(json.loads(response.data)) == 0
