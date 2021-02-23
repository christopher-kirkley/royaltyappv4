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


# def test_can_lookup_statement_summary_table(test_client, db):
#     setup_statement(test_client, db)
#     statement_summary_table = ga.lookup_statement_summary_table(1)
#     assert statement_summary_table.name == 'statement_summary_2020_01_01_2020_01_31'

# def test_can_view_statement_summary(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {
#             'summary': {
#                 'statement_total': 0,
#                 'previous_balance': None,
#                 'statement': 'statement_2020_01_01_2020_01_31',
#                 },
#             'detail':
#                 [{
#                     'id': 1,
#                     'artist_name': 'Ahmed Ag Kaedy',
#                     'balance_forward': -10229.19,
#                     'split': -686.56,
#                     'total_advance': 9542.63,
#                     'total_previous_balance': 0,
#                     'total_recoupable': 1398.06,
#                     'total_sales': 31.25,
#                     'total_to_split': -1373.11
#                     }],
#             }

# def test_can_view_statement_artist_detail(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/1/artist/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {
#             'artist': 'Ahmed Ag Kaedy',
#             'statement': 'statement_2020_01_01_2020_01_31',
#             'summary': [{
#                 'balance_forward': -10226.04,
#                 'previous_balance': 0.0,
#                 'sales': 31.25,
#                 'split': -683.41,
#                 'advances': 9542.63,
#                 'recoupables': 1398.06,
#                 'total_to_split': -1366.81
#                 }],
#             'income':
#                 [{
#                     'catalog_name': 'Akaline Kidal',
#                     'combined_net': 30.45,
#                     'digital_net': 0,
#                     'physical_net': 30.45,
#                     }],
#             'expense':
#                 [{
#                     'date': '2020-01-01',
#                     'detail': 'SS-050cd - 1049',
#                     'expense': 1398.06,
#                     'item': 'Manufacturing',
#                     'vendor': 'A to Z'
#                     }],
#             'advance':
#                 [
#                     {
#                     'date': '2020-01-01',
#                     'detail': 'Money Transfer',
#                     'expense': 897.96,
#                     'item': 'Payout',
#                     'vendor': 'Xoom.com'
#                     }, 
#                     {
#                     'date': '2020-01-01',
#                     'detail': 'SS-050lp - 2042',
#                     'expense': 8544.67,
#                     'item': 'Manufacturing',
#                     'vendor': 'A to Z'
#                     },
#                     {
#                     'date': '2020-01-01',
#                     'detail': 'Money Transfer',
#                     'expense': 100.00,
#                     'item': 'Credit',
#                     'vendor': 'Artists:Ahmed Ag Kaedy'
#                     },
#                 ],
#             'album_sales':
#                 [
#                 {
#                     'catalog_name': 'Akaline Kidal',
#                     'version_number': 'SS-050cass',
#                     'format': 'cass',
#                     'quantity': 1,
#                     'net': 10.15,
#                     },
#                 {
#                     'catalog_name': 'Akaline Kidal',
#                     'version_number': 'SS-050digi',
#                     'format': 'digital',
#                     'quantity': 1,
#                     'net': 10.15,
#                     },
#                 {
#                     'catalog_name': 'Akaline Kidal',
#                     'version_number': 'SS-050lp',
#                     'format': 'lp',
#                     'quantity': 1,
#                     'net': 10.15,
#                     },
#                 ],
#             'track_sales':
#                 [
#                 {
#                     'track_name': 'Adounia',
#                     'quantity': 1,
#                     'net': 0.8,
#                     },
#                 ],

#             }

# def test_can_view_statement_artist_detail_two_artists(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/1/artist/1')
#     assert response.status_code == 200
#     response = test_client.get('/statements/1/artist/2')
#     assert response.status_code == 200
#     data = json.loads(response.data)
#     assert data['artist'] == 'Bonehead Jones'
#     assert data['summary'] == [{
#                 'balance_forward': 0,
#                 'previous_balance': 0.0,
#                 'sales': 0,
#                 'split': 0,
#                 'advances': 0,
#                 'recoupables': 0,
#                 'total_to_split': 0
#                 }]


# def test_can_edit_statement_versions(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/1/versions')
#     assert response.status_code == 200
#     assert len(response.data) > 0
#     versions = json.loads(response.data)['versions']
#     first_version = versions[0]
#     assert first_version['catalog_name'] == 'Akaline Kidal'
#     assert first_version['format'] == 'cass'
#     assert first_version['version_number'] == 'SS-050cass'

# def test_can_delete_statement_versions(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/1/versions')
#     assert response.status_code == 200
#     versions = json.loads(response.data)['versions']
#     assert len(versions) == 3
#     response = test_client.delete('/statements/1/versions/1')
#     assert response.status_code == 200
#     response = test_client.get('/statements/1/versions')
#     assert response.status_code == 200
#     versions = json.loads(response.data)['versions']
#     assert len(versions) == 2

# def test_can_view_previous_balances(test_client, db):
#     setup_statement(test_client, db)
#     response = test_client.get('/statements/previous')
#     assert response.status_code == 200

# def test_can_update_previous_balance(test_client, db):
#     setup_statement(test_client, db)
    
#     """Check current balance forward correct."""
#     assert db.session.query(StatementGenerated).first().previous_balance_id == None
#     metadata = MetaData(db.engine, reflect=True)
#     table = metadata.tables.get('statement_2020_01_01_2020_01_31_balance')
#     assert db.session.query(table).first().balance_forward == Decimal('-10216.71')
    
#     """Modify previous balance."""
#     data = {
#             'previous_balance_id': 1
#             }
#     json_data = json.dumps(data)
#     response = test_client.put('/statements/1', data=json_data)
#     assert response.status_code == 200
#     res = db.session.query(StatementGenerated).filter(StatementGenerated.id == 1).first()
#     assert res.id == 1
#     assert res.previous_balance_id == 1
#     assert json.loads(response.data) == {'success': 'true'}

#     """Regenerate Summary."""
#     response = test_client.post('/statements/1/generate-summary')

#     """Confirm previous balance updated."""
#     metadata = MetaData(db.engine, reflect=True)
#     table = metadata.tables.get('statement_summary_2020_01_01_2020_01_31')

#     assert db.session.query(table).first().previous_balance == Decimal('-10216.71') 

