import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def import_catalog(test_client, db, case):
    path = os.getcwd() + f'/tests/api/{case}/catalog.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/api/{case}/version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/api/{case}/track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/api/{case}/bundle.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_match_version(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    assert len(db.session.query(IncomePending).all()) == 10
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '123').one()
    assert res.medium == 'digital'
    assert res.type == 'album'
    assert res.album_name == 'Amazing'
    assert res.upc_id == '2222222222'
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '456').one()
    assert res.medium == 'physical'
    assert res.upc_id is ''
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '789').one()
    assert res.version_number == 'BUNDLE1'
    assert res.upc_id =='4'

def test_can_process_pending(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 12
    id = db.session.query(Version.id).filter(Version.version_number=='TEST-01cass') 
    assert len(db.session.query(IncomeTotal).filter(IncomeTotal.version_id==id).all()) == 2

    id = db.session.query(Version.id).filter(Version.version_number=='TEST-01lp') 
    assert len(db.session.query(IncomeTotal).filter(IncomeTotal.version_id==id).all()) == 4



    
