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

def import_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/sdphysical.csv"
    data = {
            'statement_source': 'sdphysical'
            }
    data['file'] = (path, 'sdphysical.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_update_version_on_hyphen_label_credit(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.order_id=='11111').one()
    assert query.artist_name == 'Label Credit'
    assert query.version_number == 'TEST-01lp'
    assert query.upc_id == '3333333333'

def test_can_update_version_on_case_label_credit(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.order_id=='22222').one()
    assert query.artist_name == 'Label Credit'
    assert query.version_number == 'TEST-01lp'
    assert query.upc_id == '3333333333'

def test_can_update_upc_on_version(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.order_id=='33333').one()
    assert query.version_number == 'TEST-01lp'
    # assert query.upc_id == '3333333333'

def test_can_update_upc_on_version_with_no_dashes(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.order_id=='4').one()
    assert query.version_number == 'TEST-01lp'

def test_can_update_upc_on_version_with_two_dashes(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).filter(IncomePending.order_id=='5').one()
    assert query.version_number == 'TEST-01lp'
