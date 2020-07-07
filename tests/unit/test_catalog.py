import pytest
import json

from royaltyapp.models import Artist, Catalog, Version
from .helpers import add_one_artist, add_one_catalog, add_one_version

def test_can_get_all_catalog(test_client, db):
    response = test_client.get('/catalog')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0
    add_one_catalog(db)
    response = test_client.get('/catalog')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
    assert json.loads(response.data)[0]['artist']
    
def test_can_add_catalog(test_client, db):
    add_one_artist(db)
    data = {'catalog_number': 'SS-001',
            'catalog_name': 'Ishilan N-Tenere',
            'artist_id': 1
            }
    json_data = json.dumps(data)
    response = test_client.post('/catalog', data=json_data)
    assert response.status_code == 200
    result = Catalog.query.all()
    assert len(result) == 1
    assert json.loads(response.data) == {'success': 'true'}

def test_can_delete_catalog(test_client, db):
    add_one_catalog(db)
    response = test_client.delete('/catalog/1')
    assert response.status_code == 200
    result = Catalog.query.all()
    assert len(result) == 0
    assert json.loads(response.data) == {'success': 'true'}

def test_can_get_all_catalogs_by_artist(test_client, db):
    add_one_catalog(db)
    new_catalog = Catalog(catalog_number='SS-002',
                        catalog_name='Tacos for Sale',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()
    result = Catalog.query.all()
    assert len(result) == 2
    response = test_client.get('/artists/1')
    assert response.status_code == 200
    response_json = json.loads(response.data)['catalog']
    assert len(response_json) == 2

def test_can_add_version(test_client, db):
    add_one_catalog(db)
    data = {'catalog': '1',
            'version': [
                {'upc': '123456',
                'version_number': 'SS-001lp',
                'version_name': 'Limited Edition',
                'format': 'LP',
                }
                ]
        }
    json_data = json.dumps(data)
    response = test_client.post('/version', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}

def test_can_add_multiple_version(test_client, db):
    add_one_catalog(db)
    data = {'catalog': '1',
            'version': [
                {'upc': '123456',
                'version_number': 'SS-001lp',
                'version_name': 'Limited Edition',
                'format': 'LP',
                },
                {'upc': '7891011',
                'version_number': 'SS-001cass',
                'version_name': 'Limited Cassette',
                'format': 'Cassette',
                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.post('/version', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}


def test_can_get_version(test_client, db):
    add_one_version(db)
    response = test_client.get('/version/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'format': 'LP',
            'catalog_id': 1,
            'id': 1, 
            'version_number': 'SS-001lp', 
            'upc': '123456', 
            'version_name': 'Limited Vinyl'}

def test_can_get_all_versions_by_catalog(test_client, db):
    add_one_version(db)
    response = test_client.get('/catalog/1')
    assert response.status_code == 200
    json_resp = json.loads(response.data)['version']
    assert len(json_resp) == 1

def test_can_get_one_catalog_item(test_client, db):
    add_one_version(db)
    response = test_client.get('/catalog/1')
    assert response.status_code == 200
    assert json.loads(response.data)['artist']

def test_can_update_catalog(test_client, db):
    add_one_version(db)
    q = db.session.query(Catalog).first()
    data = {'catalog_number': 'SS-002',
            'catalog_name': 'Ishilan N-Tenere',
            'artist_id': 1
            }
    json_data = json.dumps(data)
    response = test_client.put('/catalog/1', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Catalog).first()
    assert q.catalog_number == 'SS-002'
