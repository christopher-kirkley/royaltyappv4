import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending

from royaltyapp.income.helpers import StatementFactory

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
    assert first.upc_id == '602318 137111'
    assert json.loads(response.data) == {'success': 'true'}
    # result = db.session.query(IncomePending).filter(IncomePending.upc_id == None).all()
    # assert len(result) > 0
    
def test_can_get_matching_errors(test_client, db):
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == {'errors': 0}
    path = os.getcwd() + "/tests/files/bandcamp_test.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp_test.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    response = test_client.get('/income/matching-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == {'errors': 732}

# def test_can_use_bandcamp_statement_factory(test_client, db):
    # path = os.getcwd() + "/tests/files/bandcamp_test.csv"
    # file = dict(file=path, filename='bandcamp_test.csv')
    # statement = StatementFactory.get_statement(path, 'bandcamp')
    # statement.create_df()
    # assert statement.file == file
    # statement.clean()
    # statement.modify_columns()
    # assert list(statement.df.columns) == statement.columns_for_db
