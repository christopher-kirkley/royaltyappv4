import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

CASE='matching_error'

def import_catalog(test_client, db, case):
    path = os.getcwd() + f'/tests/test_cases/{case}/catalog.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/test_cases/{case}/version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/test_cases/{case}/track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    assert response.status_code == 200

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/test_cases/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def import_bundle(test_client, db, case):
    path = os.getcwd() + f'/tests/test_cases/{case}/bundle.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}

def test_can_get_matching_errors(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 4

def test_can_get_bundle_matching_errors(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    assert len(db.session.query(Bundle).all()) != 0
    assert db.session.query(Bundle).first().upc == '999111'
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 3

def test_can_update_matching_errors(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    assert len(db.session.query(Bundle).all()) != 0
    assert db.session.query(Bundle).first().upc == '999111'
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 3

    """Update bundle matching errors."""
    data = {
            'error_type': 'upc',
            'selected_ids': [15],
            'new_value' : '999111'
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 2

    """Update version matching errors."""
    data = {
            'error_type': 'upc',
            'selected_ids': [11, 5],
            'new_value' : '999111'
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0
