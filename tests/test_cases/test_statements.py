import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from decimal import Decimal
from sqlalchemy import MetaData

import time

from royaltyapp.models import StatementGenerated, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending

from royaltyapp.statements.util import generate_artist_statement as ga

from helpers import import_catalog, import_bandcamp_sales

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def test_can_generate_statement(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    query = db.session.query(StatementGenerated).all()
    assert len(query) == 1
    m = MetaData()
    m.reflect(db.engine)
    table_list = [table.name for table in m.tables.values()]
    assert 'statement_2020_01_01_2020_01_31' in table_list
    assert 'statement_2020_01_01_2020_01_31_balance' in table_list
    assert 'statement_summary_2020_01_01_2020_01_31' in table_list

def test_can_delete_statement(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.delete('/statements/1')
    assert response.status_code == 200
    query = db.session.query(StatementGenerated).all()
    assert len(query) == 0
    m = MetaData()
    m.reflect(db.engine)
    table_list = [table.name for table in m.tables.values()]
    assert 'statement_2020_01_01_2020_01_31' not in table_list
    assert 'statement_2020_01_01_2020_01_31_balance' not in table_list
    assert 'statement_summary_2020_01_01_2020_01_31' not in table_list


def test_can_view_statement_summary(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 0,
                'previous_balance': 1,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                []
                }


def test_can_view_statement_versions(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.get('/statements/1/versions')
    assert response.status_code == 200
    assert len(response.data) > 0
    versions = json.loads(response.data)['versions']
    assert len(versions) == 0

def test_story(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.delete('/statements/1')
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    assert db.session.query(StatementGenerated).one().id == 2
    response = test_client.get('/statements/2/versions')
    assert response.status_code == 200
    assert len(response.data) > 0
    versions = json.loads(response.data)['versions']
    assert len(versions) == 0


def test_statement_with_data(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert len(db.session.query(IncomeTotal).all()) > 0

    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.post('/statements/1/generate-summary', data=json_data)
    assert response.status_code == 200
    assert db.session.query(StatementGenerated).one().id == 1
    response = test_client.get('/statements/1')
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 25.0,
                'previous_balance': 1,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 25.0,
                    'split': 25.0,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 50.0,
                    'total_to_split': 50.0
                    }],
            }

    response = test_client.get('/statements/1/versions')
    assert response.status_code == 200

    versions = json.loads(response.data)['versions']
    assert len(versions) == 1

    """Get artist statement info"""
    response = test_client.get('/statements/1/artist/1', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'artist': 'Bonehead',
            'statement': 'statement_2020_01_01_2020_01_31',
            'summary': [{
                'balance_forward': 25.0,
                'previous_balance': 0.0,
                'sales': 50.0,
                'split': 25.0,
                'advances': 0.0,
                'recoupables': 0.0,
                'total_to_split': 50.0
                }],
            'income':
                [{
                    'catalog_name': 'Amazing',
                    'combined_net': 50.0,
                    'digital_net': 0,
                    'physical_net': 50.0,
                    }],
            'expense':
                [],
            'advance':
                [],
            'album_sales':
                [
                {
                    'catalog_name': 'Amazing',
                    'version_number': 'TEST-01cass',
                    'format': 'cass',
                    'quantity': 1,
                    'net': 50.0,
                    },
                ],
            'track_sales':
                [
                ],

            }

def test_opening_balance_import_errors(test_client, db):
    path = os.getcwd() + f'/tests/test_cases/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200

    """ Check table created """
    metadata = MetaData(db.engine)
    metadata.reflect()
    table = metadata.tables.get('opening_balance')

    assert json.loads(response.data) == {'errors': 1}

def test_opening_balance_import_no_error(test_client, db):
    import_catalog(test_client, db, CASE)
    path = os.getcwd() + f'/tests/test_cases/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200

    """ Check table created """
    metadata = MetaData(db.engine)
    metadata.reflect()
    table = metadata.tables.get('opening_balance')

    assert len(db.session.query(table).all()) == 1
    assert db.session.query(table).all()[0].artist_id == 1

    assert json.loads(response.data) == {'success': 'true'}
