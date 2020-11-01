import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

import time

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal, ExpensePending, ExpensePendingSchema

from royaltyapp.expense.helpers import expense_matching_errors

from .helpers import build_catalog, add_artist_expense, add_order_settings

def test_can_import_artist_expense(test_client, db):
    path = os.getcwd() + "/tests/files/test1_expense_artist.csv"
    data = {
            'file': (path, 'expense_artist.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(ExpensePending).all()
    assert len(result) == 4
    first = db.session.query(ExpensePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.description == 'Money Transfer'
    assert str(first.net) == '100.00'
    assert first.item_type == 'Credit'
    assert first.expense_type == 'Advance'
    assert first.statement == 'expense_artist.csv'
    assert json.loads(response.data) == {'success': 'true'}
    
def test_can_list_pending_statements(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    response = test_client.get('/expense/pending-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
                'statement': 'expense_artist.csv'
                                        }]

def test_can_get_artist_matching_errors(test_client, db):
    response = test_client.get('/expense/artist-matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    add_artist_expense(test_client)
    response = test_client.get('/expense/artist-matching-errors')
    assert response.status_code == 200
    assert db.session.query(ExpensePending).all() != 0
    assert db.session.query(ExpensePending).first().statement == 'expense_artist.csv'
    res = json.loads(response.data)
    assert len(res) == 4
    build_catalog(db, test_client)
    response = test_client.get('/expense/artist-matching-errors')
    assert response.status_code == 200
    res = json.loads(response.data)
    assert len(res) == 2
    assert res[0] == {
            'id': 3,
            'artist_id': None,
            'artist_name': 'Les Filles de Illighadad',
            'catalog_number': None,
            'catalog_id': None,
            'date': '2020-01-01',
            'net': 673.47,
            'description': '10% of Tour – paid out of tour money',
            'expense_type': 'Advance',
            'item_type': 'Payout',
            'statement': 'expense_artist.csv',
            'vendor': 'Les Filles de Illighadad',
            }


def test_can_update_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    data = {
            'artist_name': 'Tooboo',
            'data_to_match' :
                [
                    {
                        'artist_name': 'Les Filles de Illighadad',
                    }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/expense/update-errors', data=json_data)
    query = (db.session.query(ExpensePending)
                .filter(ExpensePending.id == 3)
                .first()
                )
    assert query.artist_name == 'Tooboo'
    assert json.loads(response.data) == {'success': 'true'}


# def test_income_distributors_populated(test_client, db):
#     query = db.session.query(IncomeDistributor).all()
#     assert len(query) == 6

# def test_can_get_order_settings(test_client, db):
#     response = test_client.get('/income/order-settings')
#     assert response.status_code == 200
#     assert json.loads(response.data) == []

# def test_can_add_order_setting(test_client, db):
#     data = {
#             'distributor_id' : 1,
#             'order_percentage' : .20,
#             'order_fee' : 2.00
#             }
#     json_data = json.dumps(data)
#     response = test_client.post('/income/order-settings', data=json_data)
#     assert response.status_code == 200
#     assert json.loads(response.data) == {'success': 'true'}
#     res = db.session.query(OrderSettings).first()
#     assert res.distributor_id == 1
#     assert res.order_percentage == .20
#     assert res.order_fee == 2.00

# def test_can_edit_order_setting(test_client, db):
#     data = {
#             'distributor_id' : 1,
#             'order_percentage' : .20,
#             'order_fee' : 2.00
#             }
#     json_data = json.dumps(data)
#     response = test_client.post('/income/order-settings', data=json_data)
#     data = {
#             'distributor_id' : 1,
#             'order_percentage' : .40,
#             'order_fee' : 2.50
#             }
#     json_data = json.dumps(data)
#     response = test_client.put('/income/order-settings', data=json_data)
#     assert response.status_code == 200
#     assert json.loads(response.data) == {'success': 'true'}
#     res = db.session.query(OrderSettings).first()
#     assert res.distributor_id == 1
#     assert res.order_percentage == .40
#     assert res.order_fee == 2.50

# def test_can_process_pending_income(test_client, db):
#     build_catalog(db, test_client)
#     add_bandcamp_sales(test_client)
#     response = test_client.post('/income/process-pending')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {'success': 'true'}
#     res = db.session.query(IncomeTotal).all()
#     assert len(res) == 7

# def test_can_view_imported_statements(test_client, db):
#     build_catalog(db, test_client)
#     add_bandcamp_sales(test_client)
#     response = test_client.post('/income/process-pending')
#     response = test_client.get('/income/imported-statements')
#     assert response.status_code == 200
#     assert json.loads(response.data) == [{
#                                         'id' : 1,
#                                         'income_distributor_id' : 1,
#                                         'statement_name' : 'one_bandcamp_test.csv',
#                                         'transaction_type' : 'income'
#                                         }]


# def test_can_view_imported_statement_detail(test_client, db):
#     build_catalog(db, test_client)
#     add_bandcamp_sales(test_client)
#     add_order_settings(db)
#     response = test_client.post('/income/process-pending')
#     response = test_client.get('/income/statements/1')
#     assert response.status_code == 200
#     res = db.session.query(IncomeTotal).all()
#     assert res != 0
#     res = db.session.query(ImportedStatement).first()
#     assert res.id == 1
#     res = db.session.query(IncomeTotal).first()
#     assert res.imported_statement_id == 1
#     result = json.loads(response.data)[0]
#     assert result['number_of_records'] == 7
#     assert result['amount'] == 31.33
#     assert result['label_fee'] == 6.22
#     assert result['label_net'] == 25.11
#     assert len(result['digital']) != 0

# def test_can_delete_imported_statement(test_client, db):
#     build_catalog(db, test_client)
#     add_bandcamp_sales(test_client)
#     add_order_settings(db)
#     response = test_client.post('/income/process-pending')
#     response = test_client.get('/income/imported-statements')
#     assert response.status_code == 200
#     assert json.loads(response.data) == [{
#                                         'id' : 1,
#                                         'income_distributor_id' : 1,
#                                         'statement_name' : 'one_bandcamp_test.csv',
#                                         'transaction_type' : 'income'
#                                         }]
#     response = test_client.delete('/income/statements/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {'success': 'true'}
#     res = db.session.query(IncomeTotal).all()
#     assert len(res) == 0

