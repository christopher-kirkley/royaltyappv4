import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal, ExpensePending, ExpensePendingSchema, ExpenseType

from royaltyapp.income.helpers import StatementFactory, process_pending_statements

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense

def test_can_import_catalog_expense(test_client, db):
    path = os.getcwd() + "/tests/files/expense_catalog.csv"
    data = {
            'file': (path, 'expense_catalog.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(ExpensePending).all()
    assert len(result) == 4
    first = db.session.query(ExpensePending).first()
    assert first.date == datetime.date(2019, 9, 26)
    assert first.description == 'SS-050cd - 1049'
    assert str(first.net) == '1398.06'
    assert first.item_type == 'Manufacturing'
    assert first.statement == 'expense_catalog.csv'
    assert first.expense_type == 'Recoupable'
    assert json.loads(response.data) == {'success': 'true'}
    
def test_can_list_pending_statements(test_client, db):
    build_catalog(db, test_client)
    add_catalog_expense(test_client)
    response = test_client.get('/expense/pending-statements')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
                'statement': 'expense_catalog.csv'
                                        }]

def test_can_get_catalog_matching_errors(test_client, db):
    res = db.session.query(ExpenseType).all()
    assert len(res) != 0
    response = test_client.get('/expense/catalog-matching-errors')
    assert response.status_code == 200
    add_catalog_expense(test_client)
    response = test_client.get('/expense/catalog-matching-errors')
    assert response.status_code == 200
    assert db.session.query(ExpensePending).all() != 0
    assert db.session.query(ExpensePending).first().statement == 'expense_catalog.csv'
    res = json.loads(response.data)
    assert len(res) == 4
    build_catalog(db, test_client)
    response = test_client.get('/expense/catalog-matching-errors')
    assert response.status_code == 200
    res = json.loads(response.data)
    assert len(res) == 2

def test_can_update_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_catalog_expense(test_client)
    data = {
            'catalog_number': 'SS-050',
            'data_to_match' :
                [
                    {
                        'catalog_number': 'SS-011',
                    }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/expense/update-errors', data=json_data)
    query = (db.session.query(ExpensePending)
                .filter(ExpensePending.id == 3)
                .first()
                )
    assert query.catalog_number == 'SS-050'
    assert json.loads(response.data) == {'success': 'true'}


# # def test_income_distributors_populated(test_client, db):
# #     query = db.session.query(IncomeDistributor).all()
# #     assert len(query) == 6

# # def test_can_get_order_settings(test_client, db):
# #     response = test_client.get('/income/order-settings')
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == []

# # def test_can_add_order_setting(test_client, db):
# #     data = {
# #             'distributor_id' : 1,
# #             'order_percentage' : .20,
# #             'order_fee' : 2.00
# #             }
# #     json_data = json.dumps(data)
# #     response = test_client.post('/income/order-settings', data=json_data)
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == {'success': 'true'}
# #     res = db.session.query(OrderSettings).first()
# #     assert res.distributor_id == 1
# #     assert res.order_percentage == .20
# #     assert res.order_fee == 2.00

# # def test_can_edit_order_setting(test_client, db):
# #     data = {
# #             'distributor_id' : 1,
# #             'order_percentage' : .20,
# #             'order_fee' : 2.00
# #             }
# #     json_data = json.dumps(data)
# #     response = test_client.post('/income/order-settings', data=json_data)
# #     data = {
# #             'distributor_id' : 1,
# #             'order_percentage' : .40,
# #             'order_fee' : 2.50
# #             }
# #     json_data = json.dumps(data)
# #     response = test_client.put('/income/order-settings', data=json_data)
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == {'success': 'true'}
# #     res = db.session.query(OrderSettings).first()
# #     assert res.distributor_id == 1
# #     assert res.order_percentage == .40
# #     assert res.order_fee == 2.50

# # def test_can_process_pending_income(test_client, db):
# #     build_catalog(db, test_client)
# #     add_bandcamp_sales(test_client)
# #     response = test_client.post('/income/process-pending')
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == {'success': 'true'}
# #     res = db.session.query(IncomeTotal).all()
# #     assert len(res) == 7

# # def test_can_view_imported_statements(test_client, db):
# #     build_catalog(db, test_client)
# #     add_bandcamp_sales(test_client)
# #     response = test_client.post('/income/process-pending')
# #     response = test_client.get('/income/imported-statements')
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == [{
# #                                         'id' : 1,
# #                                         'income_distributor_id' : 1,
# #                                         'statement_name' : 'one_bandcamp_test.csv',
# #                                         'transaction_type' : 'income'
# #                                         }]


# # def test_can_view_imported_statement_detail(test_client, db):
# #     build_catalog(db, test_client)
# #     add_bandcamp_sales(test_client)
# #     add_order_settings(db)
# #     response = test_client.post('/income/process-pending')
# #     response = test_client.get('/income/statements/1')
# #     assert response.status_code == 200
# #     res = db.session.query(IncomeTotal).all()
# #     assert res != 0
# #     res = db.session.query(ImportedStatement).first()
# #     assert res.id == 1
# #     res = db.session.query(IncomeTotal).first()
# #     assert res.imported_statement_id == 1
# #     result = json.loads(response.data)[0]
# #     assert result['number_of_records'] == 7
# #     assert result['amount'] == 31.33
# #     assert result['label_fee'] == 6.22
# #     assert result['label_net'] == 25.11
# #     assert len(result['digital']) != 0

# # def test_can_delete_imported_statement(test_client, db):
# #     build_catalog(db, test_client)
# #     add_bandcamp_sales(test_client)
# #     add_order_settings(db)
# #     response = test_client.post('/income/process-pending')
# #     response = test_client.get('/income/imported-statements')
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == [{
# #                                         'id' : 1,
# #                                         'income_distributor_id' : 1,
# #                                         'statement_name' : 'one_bandcamp_test.csv',
# #                                         'transaction_type' : 'income'
# #                                         }]
# #     response = test_client.delete('/income/statements/1')
# #     assert response.status_code == 200
# #     assert json.loads(response.data) == {'success': 'true'}
# #     res = db.session.query(IncomeTotal).all()
# #     assert len(res) == 0

