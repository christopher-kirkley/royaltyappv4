import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending

from royaltyapp.income.helpers import StatementFactory, find_distinct_matching_errors

from .helpers import build_catalog, add_bandcamp_sales

def test_can_import_bandcamp_sales(test_client, db):
    path = os.getcwd() + "/tests/files/bandcamp_test.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp_test.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 732
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '602318137111'
    assert json.loads(response.data) == {'success': 'true'}
    
def test_can_get_matching_errors(test_client, db):
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    path = os.getcwd() + "/tests/files/one_bandcamp_test.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'one_bandcamp_test.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert db.session.query(IncomePending).all() != 0
    assert db.session.query(IncomePending).first().distributor == 'bandcamp'
    assert db.session.query(IncomePending).first().upc_id == '602318136817'
    assert db.session.query(IncomePending).first().catalog_id == 'SS-050'
    assert db.session.query(IncomePending).first().version_id == None

    """check function"""
    query = find_distinct_matching_errors()
    res = query.first()
    assert res.distributor == 'bandcamp'
    assert res.upc_id == '602318136817'
    assert len(json.loads(response.data)) == 6

def test_can_update_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {'version_number': 'no sku',
                    'medium': 'physical'}
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {'album_name': 'no album name'}
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    query = (db.session.query(IncomePending)

                .filter(IncomePending.id == 4)
                .first()
                )
    assert query.upc_id == '111'
    query = (db.session.query(IncomePending)
                .filter(IncomePending.id == 6)
                .first()
                )
    assert query.upc_id == 'noupc'
    query = (db.session.query(IncomePending)
                .filter(IncomePending.id == 5)
                .first()
                )
    assert query.upc_id == '111'
    assert json.loads(response.data) == {'success': 'true'}

def test_can_list_pending_statements(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.get('/income/pending-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{'distributor' : 'bandcamp',
                                        'statement': 'one_bandcamp_test.csv'
                                        }]

