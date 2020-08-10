import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal, ExpensePending, ExpensePendingSchema, ExpenseType

from royaltyapp.income.helpers import StatementFactory, find_distinct_matching_errors, process_pending_statements

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense

def test_can_process_pending_expense(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    response = test_client.post('/expense/process-pending')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(ExpenseTotal).all()
    assert len(res) == 4

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

