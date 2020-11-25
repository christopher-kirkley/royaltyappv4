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

from .helpers import build_catalog, add_artist_expense, add_bandcamp_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement, setup_test1, setup_statement


def test_can_lookup_statement_summary_table(test_client, db):
    setup_statement(test_client, db)
    statement_summary_table = ga.lookup_statement_summary_table(1)
    assert statement_summary_table.name == 'statement_summary_2020_01_01_2020_01_31'

def test_can_view_statement_summary(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 0,
                'previous_balance': None,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'id': 1,
                    'artist_name': 'Ahmed Ag Kaedy',
                    'balance_forward': -10229.19,
                    'split': -686.56,
                    'total_advance': 9542.63,
                    'total_previous_balance': 0,
                    'total_recoupable': 1398.06,
                    'total_sales': 31.25,
                    'total_to_split': -1373.11
                    }],
            }

def test_can_view_statement_artist_detail(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'artist': 'Ahmed Ag Kaedy',
            'statement': 'statement_2020_01_01_2020_01_31',
            'summary': [{
                'balance_forward': -10226.04,
                'previous_balance': 0.0,
                'sales': 31.25,
                'split': -683.41,
                'advances': 9542.63,
                'recoupables': 1398.06,
                'total_to_split': -1366.81
                }],
            'income':
                [{
                    'catalog_name': 'Akaline Kidal',
                    'combined_net': 30.45,
                    'digital_net': 0,
                    'physical_net': 30.45,
                    }],
            'expense':
                [{
                    'date': '2020-01-01',
                    'detail': 'SS-050cd - 1049',
                    'expense': 1398.06,
                    'item': 'Manufacturing',
                    'vendor': 'A to Z'
                    }],
            'advance':
                [
                    {
                    'date': '2020-01-01',
                    'detail': 'Money Transfer',
                    'expense': 897.96,
                    'item': 'Payout',
                    'vendor': 'Xoom.com'
                    }, 
                    {
                    'date': '2020-01-01',
                    'detail': 'SS-050lp - 2042',
                    'expense': 8544.67,
                    'item': 'Manufacturing',
                    'vendor': 'A to Z'
                    },
                    {
                    'date': '2020-01-01',
                    'detail': 'Money Transfer',
                    'expense': 100.00,
                    'item': 'Credit',
                    'vendor': 'Artists:Ahmed Ag Kaedy'
                    },
                ],
            'album_sales':
                [
                {
                    'catalog_name': 'Akaline Kidal',
                    'version_number': 'SS-050cass',
                    'format': 'cass',
                    'quantity': 1,
                    'net': 10.15,
                    },
                {
                    'catalog_name': 'Akaline Kidal',
                    'version_number': 'SS-050digi',
                    'format': 'digital',
                    'quantity': 1,
                    'net': 10.15,
                    },
                {
                    'catalog_name': 'Akaline Kidal',
                    'version_number': 'SS-050lp',
                    'format': 'lp',
                    'quantity': 1,
                    'net': 10.15,
                    },
                ],
            'track_sales':
                [
                {
                    'track_name': 'Adounia',
                    'quantity': 1,
                    'net': 0.8,
                    },
                ],

            }

def test_can_view_statement_artist_detail_two_artists(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    response = test_client.get('/statements/1/artist/2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['artist'] == 'Bonehead Jones'
    assert data['summary'] == [{
                'balance_forward': 0,
                'previous_balance': 0.0,
                'sales': 0,
                'split': 0,
                'advances': 0,
                'recoupables': 0,
                'total_to_split': 0
                }]


def test_can_edit_statement_versions(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1/versions')
    assert response.status_code == 200
    assert len(response.data) > 0
    versions = json.loads(response.data)['versions']
    first_version = versions[0]
    assert first_version['catalog_name'] == 'Akaline Kidal'
    assert first_version['format'] == 'cass'
    assert first_version['version_number'] == 'SS-050cass'

def test_can_delete_statement_versions(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1/versions')
    assert response.status_code == 200
    versions = json.loads(response.data)['versions']
    assert len(versions) == 3
    response = test_client.delete('/statements/1/versions/1')
    assert response.status_code == 200
    response = test_client.get('/statements/1/versions')
    assert response.status_code == 200
    versions = json.loads(response.data)['versions']
    assert len(versions) == 2

def test_can_view_previous_balances(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/previous')
    assert response.status_code == 200

def test_can_update_previous_balance(test_client, db):
    setup_statement(test_client, db)
    
    """Check current balance forward correct."""
    assert db.session.query(StatementGenerated).first().previous_balance_id == None
    metadata = MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_01_2020_01_31_balance')
    assert db.session.query(table).first().balance_forward == Decimal('-10216.71')
    
    """Modify previous balance."""
    data = {
            'previous_balance_id': 1
            }
    json_data = json.dumps(data)
    response = test_client.put('/statements/1', data=json_data)
    assert response.status_code == 200
    res = db.session.query(StatementGenerated).filter(StatementGenerated.id == 1).first()
    assert res.id == 1
    assert res.previous_balance_id == 1
    assert json.loads(response.data) == {'success': 'true'}

    """Regenerate Summary."""
    response = test_client.post('/statements/1/generate-summary')

    """Confirm previous balance updated."""
    metadata = MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_summary_2020_01_01_2020_01_31')

    assert db.session.query(table).first().previous_balance == Decimal('-10216.71') 

