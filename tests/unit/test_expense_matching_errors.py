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

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_type_expense

def test_can_import_type_expense(test_client, db):
    path = os.getcwd() + "/tests/files/expense_type.csv"
    data = {
            'file': (path, 'expense_type.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = db.session.query(ExpensePending).all()
    assert len(result) == 4
    assert json.loads(response.data) == {'success': 'true'}
    
def test_can_get_type_matching_errors(test_client, db):
    response = test_client.get('/expense/type-matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == []
    add_type_expense(test_client)
    response = test_client.get('/expense/type-matching-errors')
    assert response.status_code == 200
    assert db.session.query(ExpensePending).all() != 0
    assert db.session.query(ExpensePending).first().statement == 'expense_type.csv'
    res = json.loads(response.data)
    assert len(res) == 2
    build_catalog(db, test_client)
    response = test_client.get('/expense/type-matching-errors')
    assert response.status_code == 200
    res = json.loads(response.data)
    assert len(res) == 2

def test_can_match_errors_in_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_type_expense(test_client)
    data = {
            'expense_type': 'recoupable',
            'data_to_match' :
                [
                    {
                        'id': 3,
                    }
                ]
            }
    json_data = json.dumps(data)
    response = test_client.put('/expense/match-errors', data=json_data)
    query = (db.session.query(ExpensePending)
                .filter(ExpensePending.id == 3)
                .first()
                )
    assert response.status_code == 200
    assert len(db.session.query(ExpensePending).all()) == 4
    assert query.expense_type == 'recoupable'
    assert json.loads(response.data) == {'success': 'true'}

def test_can_update_artist_errors_in_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    data = {
            'error_type': 'artist',
            'selected_ids': [ 3 ],
            'new_value': "Ahmed Ag Kaedy"
            }
    json_data = json.dumps(data)
    response = test_client.put('/expense/update-errors', data=json_data)
    query = (db.session.query(ExpensePending)
                .filter(ExpensePending.id == 3)
                .first()
                )
    assert response.status_code == 200
    assert query.artist_name == 'Ahmed Ag Kaedy'

def test_can_update_type_errors_in_pending_table(test_client, db):
    build_catalog(db, test_client)
    add_type_expense(test_client)
    data = {
            'error_type': 'type',
            'selected_ids': [ 3 ],
            'new_value': 'Advance'
            }
    json_data = json.dumps(data)
    response = test_client.put('/expense/update-errors', data=json_data)
    query = (db.session.query(ExpensePending)
                .filter(ExpensePending.id == 3)
                .first()
                )
    assert response.status_code == 200
    assert query.expense_type == 'Advance'

