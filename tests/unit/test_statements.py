import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import StatementGenerated, StatementBalanceGenerated, StatementBalance

from royaltyapp.statements.helpers import define_artist_statement_table

from royaltyapp.statements.util import generate_statement as ge

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement


def test_can_list_statements(test_client, db):
    build_catalog(db, test_client)
    add_processed_income(test_client, db)
    add_processed_expense(test_client, db)
    response = test_client.get('/statements/view-balances')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
        'id': 1,
        'statement_balance_name': 'None'
        }]

def test_can_add_statement(test_client, db):
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(StatementGenerated).all()
    assert len(res) == 1
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 2
    res = db.session.query(StatementBalance).all()
    assert len(res) == 1

def test_can_create_new_statement_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    assert table.__tablename__ == 'statement_2020_01_01_2020_01_31'

def test_can_add_statement_to_index(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_generated = ge.add_statement_to_index(table)
    assert statement_generated.id == 1
    res = db.session.query(StatementGenerated).all()
    assert len(res) == 1

def test_can_create_new_statement_balance_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_generated = ge.add_statement_to_index(table)
    assert statement_generated.id == 1
    statement_balance_table = ge.create_statement_balance_table(table)
    assert statement_balance_table.__tablename__ == 'statement_2020_01_01_2020_01_31_balance'

def test_can_add_statement_balance_to_index(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_generated = ge.add_statement_to_index(table)
    assert statement_generated.id == 1
    statement_balance_table = ge.create_statement_balance_table(table)
    assert statement_balance_table.__tablename__ == 'statement_2020_01_01_2020_01_31_balance'
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 1
    # statement_balance_name = statement_balance_table.__tablename__
    # statement_balance_generated = StatementBalanceGenerated(
    #         statement_balance_name=statement_balance_name)
    # db.session.add(statement_balance_generated)
    # db.session.commit()

    statement_balance_generated = ge.add_statement_balance_to_index(statement_balance_table)
    assert statement_balance_generated.id == 2
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 2
    
def test_can_populate_relationship_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_index = ge.add_statement_to_index(table)
    statement_balance_table = ge.create_statement_balance_table(table)
    statement_balance_index = ge.add_statement_balance_to_index(statement_balance_table)
    assert statement_balance_index.id == 2
    ge.populate_balance_relationship_table(
            statement_index,
            statement_balance_index,
            1)
    res = db.session.query(StatementBalance).all()
    assert len(res) == 1

def test_can_list_generated_statements(test_client, db):
    build_catalog(db, test_client)
    add_processed_income(test_client, db)
    add_processed_expense(test_client, db)
    response = test_client.get('/statements/view')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    generate_statement(test_client)
    response = test_client.get('/statements/view')
    assert json.loads(response.data) == [{
        'id': 1,
        'statement_name': 'statement_2020_01_01_2020_01_31'
        }]



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

