import pytest
import json
import datetime
import time

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense, add_bandcamp_errors, add_two_bandcamp_sales

"""IMPORT TESTS"""
def make_data(filename, import_type):
    path = os.getcwd() + '/tests/files/' + filename
    data = {
            'statement_source': import_type
            }
    data['file'] = (path, filename)
    return data

def test_can_import_bandcamp(test_client, db):
    filename = 'import_bandcamp.csv'
    import_type = 'bandcamp'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 732
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '602318137111'
    assert json.loads(response.data) == {'success': 'true'}

def test_can_import_sddigital(test_client, db):
    filename = 'import_sddigital.csv'
    import_type = 'sddigital'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 13
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 25)
    assert first.upc_id == '602318136800'
    assert json.loads(response.data) == {'success': 'true'}
    
def test_can_import_sdphysical(test_client, db):
    filename = 'import_sdphysical.csv'
    import_type = 'sdphysical'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 43
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 23)
    assert first.upc_id == '999990005266'
    assert json.loads(response.data) == {'success': 'true'}

def test_can_import_shopify(test_client, db):
    filename = 'import_shopify.csv'
    import_type = 'shopify'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 4
    assert result[0].date == datetime.date(2020, 1, 1)
    assert result[0].upc_id == None
    assert result[0].version_number == 'SS-055lp'
    assert result[1].date == datetime.date(2020, 1, 6)
    assert json.loads(response.data) == {'success': 'true'}

def test_can_import_sds(test_client, db):
    filename = 'import_sds.csv'
    import_type = 'sds'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 10
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '889326664840'
    assert json.loads(response.data) == {'success': 'true'}

def test_can_import_quickbooks(test_client, db):
    filename = 'import_quickbooks.csv'
    import_type = 'quickbooks'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 2
    assert json.loads(response.data) == {'success': 'true'}

def test_can_update_upc_if_matching_version(test_client, db):
    build_catalog(db, test_client)
    path = os.getcwd() + "/tests/files/shopify_test1.csv"
    data = {
            'statement_source': 'shopify'
            }
    data['file'] = (path, 'shopify_test1.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(IncomePending).all()
    assert len(result) == 4
    first = db.session.query(IncomePending).filter(IncomePending.id == 1).one()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == None
    assert first.version_number == 'SS-055lp'
    second = db.session.query(IncomePending).filter(IncomePending.id == 2).one()
    assert second.date == datetime.date(2020, 1, 6)
    assert second.upc_id == '602318136794'
    assert second.version_number == 'SS-050lp'
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
    query = find_distinct_version_matching_errors()
    res = query.first()
    assert res.distributor == 'bandcamp'
    assert res.upc_id == '602318136817'
    assert len(json.loads(response.data)) == 6

def test_can_get_track_matching_errors(test_client, db):
    build_catalog(db, test_client)
    response = test_client.get('/income/track-matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    path = os.getcwd() + "/tests/files/sd_digital_test1.csv"
    data = {
            'statement_source': 'sddigital'
            }
    data['file'] = (path, 'sd_digital_test1.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert db.session.query(IncomePending).all() != 0
    assert db.session.query(IncomePending).first().distributor == 'sddigital'
    assert db.session.query(IncomePending).first().upc_id == '602318136800'
    assert db.session.query(IncomePending).first().isrc_id == 'QZDZE1905001'
    assert db.session.query(IncomePending).first().catalog_id == None
    assert db.session.query(IncomePending).first().version_id == None

    query = find_distinct_track_matching_errors()
    assert len(query.all()) == 1

    """check function"""
    query = find_distinct_track_matching_errors()
    res = query.first()
    assert res.distributor == 'sddigital'
    assert res.isrc_id == 'QZDZE1905x03'

def test_can_update_track_matching_errors(test_client, db):
    build_catalog(db, test_client)
    path = os.getcwd() + "/tests/files/sd_digital_test1.csv"
    data = {
            'statement_source': 'sddigital'
            }
    data['file'] = (path, 'sd_digital_test1.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    data = {
            'isrc_id': 'QZDZE1905003',
            'data_to_match' :
                [
                    {
                        'isrc_id': 'QZDZE1905x03',
                        }
                ]

            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-track-errors', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'updated': 1}

def test_can_update_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {
                        'version_number': '1',
                        'medium': 'physical'}
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert len(db.session.query(IncomePending).all()) > 0
    data = {
            'upc_id': '111',
            'data_to_match' :
                [
                    {'medium': 'physical'}
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'updated': 3}

def test_can_list_pending_statements(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.get('/income/pending-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{'distributor' : 'bandcamp',
                                        'statement': 'one_bandcamp_test.csv'
                                        }]

def test_can_delete_pending_statement(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.delete('/income/pending-statements/one_bandcamp_test.csv')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    assert len(db.session.query(IncomePending).all()) == 0

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
    assert json.loads(response.data) == {
                                     'bandcamp':
                                        [{
                                            'id' : 1,
                                            'statement_name' : 'one_bandcamp_test.csv',
                                            'start_date' : '2020-01-01',
                                            'end_date' : '2020-01-04',
                                        }
                                        ],
                                    'quickbooks': [],
                                    'sds': [],
                                    'sddigital': [],
                                    'sdphysical': [],
                                    'shopify': [],
                                        }
    add_two_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    response = test_client.post('/expense/process-pending')
    response = test_client.get('/income/imported-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == {
                                     'bandcamp':
                                        [{
                                            'id' : 1,
                                            'statement_name' : 'one_bandcamp_test.csv',
                                            'start_date' : '2020-01-01',
                                            'end_date' : '2020-01-04'
                                        },
                                        {
                                            'id' : 3,
                                            'statement_name' : 'two_bandcamp_test.csv',
                                            'start_date' : '2020-01-01',
                                            'end_date' : '2020-01-01'
                                        }
                                        ],
                                    'quickbooks': [],
                                    'sds': [],
                                    'sddigital': [],
                                    'sdphysical': [],
                                    'shopify': [],
                                        }

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

