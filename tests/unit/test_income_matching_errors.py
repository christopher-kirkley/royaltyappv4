import pytest
import json
import datetime

import time
import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_bandcamp_order_settings, add_artist_expense, add_bandcamp_errors

def test_can_get_matching_errors(test_client, db):
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    path = os.getcwd() + "/tests/files/test_bandcamp_errors.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'test_bandcamp_errors.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert len(db.session.query(IncomePending).all()) != 0
    assert db.session.query(IncomePending).first().distributor == 'bandcamp'
    assert db.session.query(IncomePending).first().upc_id == '1'
    assert db.session.query(IncomePending).first().catalog_id == '1'
    assert db.session.query(IncomePending).first().version_id == None

    """check function"""
    query = find_distinct_matching_errors()
    res = query.first()
    assert res.distributor == 'bandcamp'
    assert res.upc_id == '1'
    assert len(json.loads(response.data)) == 14

def test_can_update_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_errors(test_client)
    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {
                        'version_number': '1',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 1).first()
    assert query.version_number == '1'

    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {
                        'catalog_id': '2',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 2).first()
    assert query.catalog_id == '2'
    assert query.upc_id == '111'

    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {
                        'catalog_id': 'x',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 3).first()
    assert query.catalog_id == 'x'
    assert query.upc_id == '111'

    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {
                        'description': 'French',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 12).first()
    assert query.description == 'French'
    assert query.upc_id == '111'

    data = {
            'upc_id': '123',
            'data_to_match' :
                [
                    {
                        'medium': 'physical',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 13).first()
    assert query.upc_id == '123'

    data = {
            'upc_id': '123',
            'data_to_match' :
                [
                    {
                        'upc_id': '6',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 6).first()
    assert query.upc_id == '123'
    assert query.catalog_id == '6'

    data = {
            'upc_id': '101',
            'data_to_match' :
                [
                    {
                        'type': 'track',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 13).first()
    assert query.upc_id == '123'
    query = db.session.query(IncomePending).filter(IncomePending.id == 14).first()
    assert query.upc_id == '101'
    assert query.catalog_id == None
    assert query.isrc_id == 'QZDZE1905002'

    data = {
            'upc_id': '123',
            'data_to_match' :
                [
                    {
                        'distributor': 'bandcamp',
                        }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert json.loads(response.data) == {"success": "true"}
    query = db.session.query(IncomePending).filter(IncomePending.id == 13).first()
    assert query.upc_id == '123'

def test_can_update_upc_errors_in_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    data = {
            'error_type': 'upc',
            'selected_ids': [ 1 ],
            'new_value': '602318136817'
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    query = (db.session.query(IncomePending)
                .filter(IncomePending.id == 1)
                .first()
                )
    assert response.status_code == 200
    assert query.upc_id == '602318136817'

def test_can_update_isrc_errors_in_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    data = {
            'error_type': 'isrc',
            'selected_ids': [ 1 ],
            'new_value': 'QZDZE19050016'
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    query = (db.session.query(IncomePending)
                .filter(IncomePending.id == 1)
                .first()
                )
    assert response.status_code == 200
    assert query.isrc_id == 'QZDZE19050016'

