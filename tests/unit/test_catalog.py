import pytest
import json

from royaltyapp.models import Artist, Catalog

def add_one_artist(db):
    new_artist = Artist(artist_name='Amanar',
                        prenom='Ahmed',
                        surnom='Ag Kaedi',
                        )
    db.session.add(new_artist)
    db.session.commit()

def add_one_catalog(db):
    new_catalog = Catalog(catalog_number='SS-001',
                        catalog_name='Ishilan N-Tenere',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()

def test_can_get_all_catalog(test_client, db):
    response = test_client.get('/catalog')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0

def test_can_add_catalog(test_client, db):
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


