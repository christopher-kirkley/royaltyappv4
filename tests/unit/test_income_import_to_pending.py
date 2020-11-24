import pytest
import json
import datetime
import time
from decimal import Decimal

import os
import io

import pandas as pd
import numpy as np

from sqlalchemy import func

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense, add_bandcamp_errors, add_two_bandcamp_sales

def make_data(filename, import_type):
    path = os.getcwd() + '/tests/files/' + filename
    data = {
            'statement_source': import_type
            }
    data['file'] = (path, filename)
    return data

bandcamp_cases = {
        'import_bandcamp.csv': ('import_bandcamp.csv', {'records': 732, 'sum': 4626.58}),
        'import_bandcamp_2.csv': ('import_bandcamp_2.csv', {'records': 15, 'sum': 111.24}),
        }

@pytest.mark.parametrize('filename, expected', list(bandcamp_cases.values()), ids=list(bandcamp_cases.keys()))
def test_can_import_bandcamp(test_client, db, filename, expected):
    import_type = 'bandcamp'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    assert response.status_code == 201

    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert float(total) == expected['sum']

def test_can_import_sddigital(test_client, db):
    filename = 'import_sddigital.csv'
    import_type = 'sddigital'
    data = make_data(filename, import_type)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

    """ Check response """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    records = 13
    assert response_data['data']['attributes']['length'] == records
    assert response_data['data']['attributes']['title'] == filename

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == records
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 25)
    assert first.upc_id == '602318136800'
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert round(float(total), 2) == 7.53

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

