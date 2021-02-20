import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

CASE='income_bandcamp'

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

def test_can_match_digital_version(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    assert len(db.session.query(IncomePending).all()) == 35
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '123').one()
    assert res.medium == 'digital'
    assert res.type == 'album'
    assert res.album_name == 'Amazing'
    assert res.upc_id == '2222222222'
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '456').one()
    assert res.medium == 'physical'
    assert res.upc_id is None
