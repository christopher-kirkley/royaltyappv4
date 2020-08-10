import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import *

from royaltyapp.income.helpers import StatementFactory, find_distinct_matching_errors, process_pending_statements

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense

def test_can_list_statements(test_client, db):
    build_catalog(db, test_client)
    add_processed_income(test_client, db)
    add_processed_expense(test_client, db)
    response = test_client.get('/statements/view')
    assert response.status_code == 200
    assert json.loads(response.data) == []

    # assert json.loads(response.data) == {'success': 'true'}
    # res = db.session.query(ExpenseTotal).all()
    # assert len(res) == 4

# def test_can_view_imported_statements(test_client, db):
#     build_catalog(db, test_client)
#     add_artist_expense(test_client)
#     response = test_client.post('/expense/process-pending')
#     response = test_client.get('/expense/imported-statements')
#     assert response.status_code == 200


# def test_can_view_imported_statement_detail_artist(test_client, db):
#     build_catalog(db, test_client)
#     add_artist_expense(test_client)
#     response = test_client.post('/expense/process-pending')
#     response = test_client.get('/expense/statements/1')
#     assert response.status_code == 200
#     res = db.session.query(ExpenseTotal).all()
#     assert res != 0
#     res = db.session.query(ImportedStatement).first()
#     assert res.id == 1
#     res = db.session.query(ExpenseTotal).first()
#     assert res.imported_statement_id == 1
#     result = json.loads(response.data)[0]
#     assert result['number_of_records'] == 4 
#     assert result['data'][0] == {
#             'id': 1,
#             'date': '2019-10-21',
#             'description': 'Money Transfer',
#             'item_type': 'Credit',
#             'net': 100.0,
#             'transaction_type': 'expense',
#             'vendor': 'Artists:Ahmed Ag Kaedy',
#             'artist': {'artist_name': 'Ahmed Ag Kaedy',
#                         'id': 1,
#                         },
#             'catalog': None,
#             }

# def test_can_view_imported_statement_detail_catalog(test_client, db):
#     build_catalog(db, test_client)
#     add_catalog_expense(test_client)
#     response = test_client.post('/expense/process-pending')
#     response = test_client.get('/expense/statements/1')
#     assert response.status_code == 200
#     res = db.session.query(ExpenseTotal).all()
#     assert res != 0
#     res = db.session.query(ImportedStatement).first()
#     assert res.id == 1
#     res = db.session.query(ExpenseTotal).first()
#     assert res.imported_statement_id == 1
#     result = json.loads(response.data)[0]
#     assert result['number_of_records'] == 4 
#     assert result['data'][0] == {
#             'id': 1,
#             'date': '2019-09-26',
#             'description': 'SS-050cd - 1049',
#             'item_type': 'Manufacturing',
#             'net': 1398.06,
#             'transaction_type': 'expense',
#             'vendor': 'A to Z',
#             'artist': None,
#             'catalog': {
#                 'catalog_name': 'Akaline Kidal',
#                 'catalog_number': 'SS-050',
#                 'id': 1,
#                 }
#             }

# def test_can_delete_imported_statement(test_client, db):
#     build_catalog(db, test_client)
#     add_catalog_expense(test_client)
#     response = test_client.post('/expense/process-pending')
#     response = test_client.delete('/expense/statements/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {'success': 'true'}
#     res = db.session.query(ExpenseTotal).all()
#     assert len(res) == 0

