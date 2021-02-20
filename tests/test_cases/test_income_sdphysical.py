import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

CASE='income_sdphysical'

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

def import_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/test_cases/{case}/sdphysical.csv"
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
    assert query.upc_id == '3333333333'
    assert query.version_number == 'TEST-01lp'

# def test_can_get_matching_errors(test_client, db):
#     import_catalog(test_client, db, CASE)
#     import_sales(test_client, db, CASE)
#     response = test_client.get('/income/matching-errors')
#     assert response.status_code == 200
#     assert len(json.loads(response.data)) == 0

