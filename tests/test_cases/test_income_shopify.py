import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

CASE='income_shopify'

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
    path = os.getcwd() + f"/tests/test_cases/{case}/bundle.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200

def import_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/test_cases/{case}/shopify.csv"
    data = {
            'statement_source': 'shopify'
            }
    data['file'] = (path, 'shopify.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_update_bundle_number(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.version_number=='unnamed bundle').all()
    assert len(query) == 1
    """Get one error"""
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
    """Update matching error"""
    data = {
            'error_type': 'upc',
            'selected_ids': [ 4 ],
            'new_value': '4'
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    query = (db.session.query(IncomePending)
                .filter(IncomePending.id == 4)
                .first()
                )
    assert response.status_code == 200
    assert query.upc_id == '4'

    """Check no errors."""
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0

    """Process errors"""
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 6

    
def test_can_process_pending(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 5
    id = db.session.query(Version.id).filter(Version.version_number=='TEST-01cass') 
    assert len(db.session.query(IncomeTotal).filter(IncomeTotal.version_id==id).all()) == 1

    id = db.session.query(Version.id).filter(Version.version_number=='TEST-01lp') 
    assert len(db.session.query(IncomeTotal).filter(IncomeTotal.version_id==id).all()) == 3



    
