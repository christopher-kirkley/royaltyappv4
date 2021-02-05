import pytest
import json

from royaltyapp.models import Artist, Catalog, Version, Track, Bundle, BundleVersionTable
from .helpers import add_one_artist, add_one_catalog, add_one_version,\
        add_one_track, add_second_artist, add_two_version, add_one_bundle

def test_can_get_all_bundles(test_client, db):
    response = test_client.get('/bundle')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0
    add_one_catalog(db)
    response = test_client.get('/bundle')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
    
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

def test_can_add_bundle_versions(test_client, db):
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
    data = {'bundle_id': '1',
            'bundle_version': [
                {
                    'version_id': '1'
                    },
                {
                    'version_id': '2'
                    },
                ]
            }
    json_data = json.dumps(data)
    response = test_client.post('/bundle/version', data=json_data)
    assert response.status_code == 200
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 2
    assert json.loads(response.data) == {'success': 'true'}

def test_can_get_bundle(test_client, db):
    add_one_bundle(test_client, db)
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 2
    response = test_client.get('/bundle/1')
    assert response.status_code == 200
    assert (json.loads(response.data)['id']) == 1
    assert (json.loads(response.data)['bundle_number']) == 'SS-TESTBUNDLE'
    assert len(json.loads(response.data)['version_bundle']) == 2

def test_can_delete_bundle(test_client, db):
    add_one_bundle(test_client, db)
    response = test_client.delete('/bundle/1')
    assert response.status_code == 200
    result = Bundle.query.all()
    assert len(result) == 0
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 0
    assert json.loads(response.data) == {'success': 'true'}

def test_can_edit_bundle(test_client, db):
    add_one_bundle(test_client, db)
    result = Bundle.query.all()
    assert len(result) == 1
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 2

    """Edit one version"""
    data = {'bundle_id': '1',
            'bundle_number': 'SS-MYS1',
            'bundle_name': 'MYSTERY1',
            'bundle_version': [
                {
                'version_id': '2',
                }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/bundle', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 1
    query = db.session.query(Bundle).filter(Bundle.id==1).first()
    assert query.bundle_number == 'SS-MYS1'
    assert query.bundle_name== 'MYSTERY1'

    """Edit again"""
    data = {'bundle_id': '1',
            'bundle_number': 'SS-MYS2',
            'bundle_name': 'MYSTERY2',
            'bundle_version': [
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/bundle', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    result = db.session.query(BundleVersionTable).all()
    assert len(result) == 0
    query = db.session.query(Bundle).filter(Bundle.id==1).first()
    assert query.bundle_number == 'SS-MYS2'
    assert query.bundle_name== 'MYSTERY2'
