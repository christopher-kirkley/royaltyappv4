import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, find_distinct_matching_errors, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense

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
    assert len(json.loads(response.data)) == 7

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

def test_income_distributors_populated(test_client, db):
    query = db.session.query(IncomeDistributor).all()
    assert len(query) == 6

def test_can_get_order_settings(test_client, db):
    response = test_client.get('/income/order-settings')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_can_add_order_setting(test_client, db):
    data = {
            'distributor_id' : 1,
            'order_percentage' : .20,
            'order_fee' : 2.00
            }
    json_data = json.dumps(data)
    response = test_client.post('/income/order-settings', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(OrderSettings).first()
    assert res.distributor_id == 1
    assert res.order_percentage == .20
    assert res.order_fee == 2.00

def test_can_edit_order_setting(test_client, db):
    data = {
            'distributor_id' : 1,
            'order_percentage' : .20,
            'order_fee' : 2.00
            }
    json_data = json.dumps(data)
    response = test_client.post('/income/order-settings', data=json_data)
    data = {
            'distributor_id' : 1,
            'order_percentage' : .40,
            'order_fee' : 2.50
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/order-settings', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(OrderSettings).first()
    assert res.distributor_id == 1
    assert res.order_percentage == .40
    assert res.order_fee == 2.50

def test_can_process_pending_income(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 7

def test_can_view_imported_statements(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    add_artist_expense(test_client)
    response = test_client.post('/income/process-pending')
    response = test_client.post('/expense/process-pending')
    response = test_client.get('/income/imported-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
                                        'id' : 1,
                                        'income_distributor_id' : 1,
                                        'statement_name' : 'one_bandcamp_test.csv',
                                        'transaction_type' : 'income'
                                        }]


def test_can_view_imported_statement_detail(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    add_order_settings(db)
    response = test_client.post('/income/process-pending')
    response = test_client.get('/income/statements/1')
    assert response.status_code == 200
    res = db.session.query(IncomeTotal).all()
    assert res != 0
    res = db.session.query(ImportedStatement).first()
    assert res.id == 1
    res = db.session.query(IncomeTotal).first()
    assert res.imported_statement_id == 1
    result = json.loads(response.data)[0]
    assert result['number_of_records'] == 7
    assert result['amount'] == 31.33
    assert result['label_fee'] == 6.22
    assert result['label_net'] == 25.11
    assert len(result['digital']) != 0

def test_can_delete_imported_statement(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    add_order_settings(db)
    response = test_client.post('/income/process-pending')
    response = test_client.get('/income/imported-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
                                        'id' : 1,
                                        'income_distributor_id' : 1,
                                        'statement_name' : 'one_bandcamp_test.csv',
                                        'transaction_type' : 'income'
                                        }]
    response = test_client.delete('/income/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 0

