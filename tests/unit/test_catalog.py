import pytest
import json

from royaltyapp.models import Artist, Catalog, Version, Track
from .helpers import add_one_artist, add_one_catalog, add_one_version,\
        add_one_track, add_second_artist

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
                {
                'upc': '123456',
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
                {
                'upc': '123456',
                'version_number': 'SS-001lp',
                'version_name': 'Limited Edition',
                'format': 'LP',
                },
                {
                'upc': '7891011',
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

def test_can_edit_versions(test_client, db):
    add_one_catalog(db)
    data = {'catalog': '1',
            'version': [
                {
                'upc': '123456',
                'version_number': 'SS-001lp',
                'version_name': 'Limited Edition',
                'format': 'LP',
                },
                {
                'upc': '7891011',
                'version_number': 'SS-001cass',
                'version_name': 'Limited Cassette',
                'format': 'Cassette',
                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.post('/version', data=json_data)
    assert response.status_code == 200
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    data = {'catalog': '1',
            'version': [
                {
                'id': '1',
                'upc': '333333',
                'version_number': 'SS-001cd',
                'version_name': 'Compact Disc',
                'format': 'CD',
                },
                {
                'id': '2',
                'upc': '7891011',
                'version_number': 'SS-001cass',
                'version_name': 'Limited Cassette',
                'format': 'Cassette',
                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/version', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    q = db.session.query(Version).order_by(Version.id).all()
    assert len(q) == 2
    assert q[0].upc == '333333'
    assert q[0].id == 1
    assert q[0].version_number == 'SS-001cd'

def test_can_remove_versions(test_client, db):
    add_one_catalog(db)
    data = {'catalog': '1',
            'version': [
                {
                'upc': '123456',
                'version_number': 'SS-001lp',
                'version_name': 'Limited Edition',
                'format': 'LP',
                },
                {
                'upc': '7891011',
                'version_number': 'SS-001cass',
                'version_name': 'Limited Cassette',
                'format': 'Cassette',
                }
                ]}
    json_data = json.dumps(data)
    response = test_client.post('/version', data=json_data)
    assert response.status_code == 200

    new_catalog = Catalog(catalog_number='SS-002',
                        catalog_name='Tacos for Sale',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()
    new_version = Version(catalog_id='2',
            version_number='SS-002lp',
            upc='1232',
            version_name='testlp',
            format='vinyl',
            )
    db.session.add(new_version)
    db.session.commit()

    res = db.session.query(Version).all()
    assert len(res)==3


    data = {'catalog': '1',
            'version': [
                {
                'id': '1',
                'upc': '333333',
                'version_number': 'SS-001cd',
                'version_name': 'Compact Disc',
                'format': 'CD',
                },
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/version', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Version).order_by(Version.id).filter(Version.catalog_id==1).all()
    assert len(q) == 1
    data = {'catalog': '1',
            'version': [
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/version', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Version).order_by(Version.id).filter(Version.catalog_id==1).all()
    assert len(q) == 0

    res = db.session.query(Version).all()
    assert len(res)==1


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

def test_can_add_second_version(test_client, db):
    add_one_version(db)
    new_catalog = Catalog(catalog_number='SS-002',
                        catalog_name='Tacos for Sale',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()
    res = db.session.query(Catalog).all()
    assert len(res) == 2
    res = db.session.query(Version).all()
    assert len(res) == 1

    """Add second version."""
    data = {'catalog': '2',
            'version': [
                {
                'upc': '7891011',
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
    res = db.session.query(Version).all()
    assert len(res) == 2

def test_can_edit_second_version(test_client, db):
    add_one_version(db)
    new_catalog = Catalog(catalog_number='SS-002',
                        catalog_name='Tacos for Sale',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()
    res = db.session.query(Catalog).all()
    assert len(res) == 2
    res = db.session.query(Version).all()
    assert len(res) == 1

    """Add second version."""
    data = {'catalog': '2',
            'version': [
                {
                'upc': '7891011',
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
    res = db.session.query(Version).all()
    assert len(res) == 2

    """Edit second version."""
    data = {'catalog': '2',
            'version': [
                {
                'id': '2',
                'upc': '7891011',
                'version_number': 'SS-001cass',
                'version_name': 'Limited Cassette',
                'format': 'Cassette',
                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/version', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}

    res = db.session.query(Version).all()
    assert len(res) == 2



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
    add_second_artist(db)
    q = db.session.query(Catalog).first()

    data = {'catalog_number': 'SS-002',
            'catalog_name': 'Ishilan Jones',
            'artist_id': 2
            }
    json_data = json.dumps(data)
    response = test_client.put('/catalog/1', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Catalog).first()
    assert q.catalog_number == 'SS-002'
    assert q.catalog_name == 'Ishilan Jones'
    assert q.artist_id == 2

def test_can_add_track(test_client, db):
    add_one_catalog(db)
    data = {
            'catalog': '1',
            'track': [
                {'track_number': '1',
                'track_name': 'Beans',
                'isrc': 'abc',
                'artist_id': 1
                }]
            }
    json_data = json.dumps(data)
    response = test_client.post('/track', data=json_data)
    assert response.status_code == 200
    q = db.session.query(Track).first()
    assert q.track_number == 1
    assert q.track_name == 'Beans'
    assert q.isrc == 'abc'
    assert q.artist_id == 1
    q = db.session.query(Catalog).first()
    query_tracks = q.tracks
    assert len(query_tracks) == 1
    assert query_tracks[0].track_number == 1
    assert query_tracks[0].track_name == 'Beans'
    assert query_tracks[0].artist_id == 1
    assert query_tracks[0].id == 1
    assert json.loads(response.data) == {'success': 'true'}

def test_can_get_catalog_tracks(test_client, db):
    add_one_track(db)
    tracks = db.session.query(Track).all()
    assert len(tracks) == 1
    response = test_client.get('/catalog/1')
    assert response.status_code == 200
    json_resp = json.loads(response.data)
    track_result = json_resp['tracks']
    assert len(track_result) == 1
    assert track_result[0] == {'track_number': 1,
                                'track_name': 'Potatoes for Sale',
                                'isrc': 'abc123',
                                'artist_id': 1,
                                'id': 1
                                }
    
def test_can_edit_track(test_client, db):
    add_one_track(db)
    data = {'catalog': '1',
            'tracks': [
                {'id': 1,
                'track_number': 2,
                'track_name': 'Tacos for Sale',
                'isrc': 'qwe123',
                'artist_id': 1
                                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/track', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    q = db.session.query(Track).first()
    assert q.track_name == 'Tacos for Sale'
    assert q.isrc == 'qwe123'
    assert q.track_number == 2

def test_can_get_all_versions(test_client, db):
    add_one_version(db)
    response = test_client.get('/version')
    assert response.status_code == 200
    json_resp = json.loads(response.data)
    assert len(json_resp) == 1
    assert json_resp == ''

def test_can_get_all_tracks(test_client, db):
    add_one_track(db)
    response = test_client.get('/tracks')
    assert response.status_code == 200
    json_resp = json.loads(response.data)
    assert len(json_resp) == 1

