import pytest
import json

from royaltyapp.models import Artist, Catalog, Version, Track, Bundle
from .helpers import add_one_artist, add_one_catalog, add_one_version,\
        add_one_track, add_second_artist, add_two_version

def test_can_get_all_bundles(test_client, db):
    response = test_client.get('/bundle')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0
    add_one_catalog(db)
    response = test_client.get('/bundle')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
    assert json.loads(response.data)[0]['artist']
    
def test_can_add_bundle(test_client, db):
    add_one_artist(db)
    add_one_catalog(db)
    add_two_version(db)
    data = {'bundle_number': 'SS-TESTBUNDLE',
            'bundle_name': 'Two Versions',
            }
    json_data = json.dumps(data)
    response = test_client.post('/bundle', data=json_data)
    assert response.status_code == 200
    result = Bundle.query.all()
    assert len(result) == 1
    assert json.loads(response.data) == {'id': 1, 'success': 'true'}

def test_can_delete_bundle(test_client, db):
    add_one_catalog(db)
    response = test_client.delete('/bundle/1')
    assert response.status_code == 200
    result = Catalog.query.all()
    assert len(result) == 0
    assert json.loads(response.data) == {'success': 'true'}

