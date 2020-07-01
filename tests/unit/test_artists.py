import pytest
import json
from flask import jsonify

from royaltyapp.models import Artist

def add_one_artist(db):
    new_artist = Artist(artist_name='Amanar',
                        prenom='Ahmed',
                        surnom='Ag Kaedi',
                        )
    db.session.add(new_artist)
    db.session.commit()

def test_can_get_all_artists(test_client, db):
    response = test_client.get('/artists')
    assert response.status_code == 200
    add_one_artist(db)
    response = test_client.get('/artists')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
                                        "id": 1, 
                                        "artist_name": "Amanar",
                                        "prenom": "Ahmed",
                                        "surnom": "Ag Kaedi",
                                        "catalog": [],
                                        }]


def test_can_add_artist(test_client, db):
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

def test_one(test_client, db):
    add_one_artist(db)
    result = Artist.query.all()
    assert len(result) == 1

def test_can_delete_artist(test_client, db):
    add_one_artist(db)
    q = db.session.query(Artist).first()
    id_to_delete = q.id
    resp = test_client.delete(f'/artists/delete/{id_to_delete}')
    assert resp.status_code == 200
    result = db.session.query(Artist).all()
    assert len(result) == 0
    assert json.loads(resp.data) == {'success': 'true'}

def test_can_update_artists(test_client, db):
    add_one_artist(db)
    q = db.session.query(Artist).first()
    assert q.artist_name == 'Amanar'
    # Change first name
    data = {
            'artist_name': 'Bobo',
            'prenom': 'Tom',
            'surnom': 'Jones',
            }
    json_data = json.dumps(data)
    response = test_client.put('/artists/1', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Artist).first()
    assert q.artist_name == 'Bobo'
    assert q.prenom == 'Tom'
    assert q.surnom == 'Jones'
    
def test_can_get_one_artist(test_client, db):
    add_one_artist(db)
    response = test_client.get('/artists/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
                                        "id": 1,
                                        "artist_name": "Amanar",
                                        "prenom": "Ahmed",
                                        "surnom": "Ag Kaedi",
                                        "catalog": []
                                        }

    

