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
    data = {
            'previous_balance_id': 0,
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

def test_can_list_generated_statements(test_client, db):
    """ Check empty list of statements. """
    response = test_client.get('/statements')
    assert response.status_code == 200
    assert json.loads(response.data) == []

    """ Check list with generated statement. """
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.get('/statements')
    assert json.loads(response.data) == [{
        'id': 1,
        'statement_detail_table': 'statement_2020_01_01_2020_01_31',
        'statement_summary_table': 'statement_summary_2020_01_01_2020_01_31'
        }]

    """ Add opening balance statement, verify opening doesn't show up """
    import_catalog(test_client, db, CASE)
    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200
    response = test_client.get('/statements')
    assert json.loads(response.data) == [{
        'id': 1,
        'statement_detail_table': 'statement_2020_01_01_2020_01_31',
        'statement_summary_table': 'statement_summary_2020_01_01_2020_01_31'
        }]

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
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.delete('/statements/1')
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 0,
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


def test_statement_with_data_no_previous_balance(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    assert len(db.session.query(IncomeTotal).all()) > 0

    data = {
            'previous_balance_id': 0,
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
                'previous_balance': 0,
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
    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
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

    response = test_client.get('/statements/opening-balance-errors')
    assert response.status_code == 200
    assert json.loads(response.data) == [
            {
                'id': 1,
                'artist_name': 'Bonehead',
                'balance_forward': '100.00',
                }]

def test_opening_balance_fix_import_errors(test_client, db):
    import_catalog(test_client, db, CASE)
    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance_errors.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200

    metadata = MetaData(db.engine)
    metadata.reflect()
    table = metadata.tables.get('opening_balance')

    assert len(db.session.query(table).all()) == 2
    id = db.session.query(table).filter(table.c.artist_name == 'Bondhead').first().id
    assert db.session.query(table).filter(table.c.id == id).first().artist_id == None

    """ Fix error."""
    data = {
            'id': 2,
            'artist_id': '1'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/opening-balance-errors',
            data=json_data)
    assert response.status_code == 200

    assert db.session.query(table).filter(table.c.id == id).first().artist_id == 1

def test_opening_balance_import_second_import(test_client, db):
    import_catalog(test_client, db, CASE)
    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200

    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200

def test_opening_balance_import(test_client, db):
    import_catalog(test_client, db, CASE)
    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
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
    
    """ Check table was added to Statement Generated """
    res = db.session.query(StatementGenerated).one()
    assert res.statement_balance_table == 'opening_balance'

    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    res = db.session.query(StatementGenerated).all()[1]
    assert res.previous_balance_id == 1 

def test_statement_with_data_with_previous_balance(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)

    path = os.getcwd() + f'/tests/api/{CASE}/opening_balance.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/statements/import-opening-balance',
            data=data)
    assert response.status_code == 200
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    res = db.session.query(StatementGenerated).all()[1]
    assert res.previous_balance_id == 1 
    assert res.id == 2

    response = test_client.post('/statements/2/generate-summary')
    assert response.status_code == 200

    response = test_client.get('/statements/2')
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 125.0,
                'previous_balance': 1,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 125.0,
                    'split': 25.0,
                    'total_advance': 0.0,
                    'total_previous_balance': 100.0,
                    'total_recoupable': 0.0,
                    'total_sales': 50.0,
                    'total_to_split': 50.0
                    }],
            }

def test_can_export_csv(test_client, db):
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.get('/statements/export-csv')
    assert response.status_code == 200
