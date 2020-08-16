import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from decimal import Decimal

import time

from royaltyapp.models import StatementGenerated, StatementBalanceGenerated, StatementBalance, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending

from royaltyapp.statements.helpers import define_artist_statement_table

from royaltyapp.statements.util import generate_artist_statement as ga

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement, setup_test1, setup_statement


def test_can_view_statement_detail(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {'statement_total': 0},
            'detail':
                [{
                    'id': 1,
                    'artist_name': 'Ahmed Ag Kaedy',
                    'balance_forward': -10229.19,
                    'split': -686.56,
                    'total_advance': 9542.63,
                    'total_previous_balance': 0,
                    'total_recoupable': 1398.06,
                    'total_sales': 24.95,
                    'total_to_split': -1373.11
                    }],
            }

def test_can_view_statement_artist_detail(test_client, db):
    setup_statement(test_client, db)
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'income':
                [{
                    'catalog_name': 'Akaline Kidal',
                    'combined_net': 24.15,
                    'digital_net': 0,
                    'physical_net': 24.15,
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
                    'net': 8.05,
                    },
                {
                    'catalog_name': 'Akaline Kidal',
                    'version_number': 'SS-050digi',
                    'format': 'digital',
                    'quantity': 1,
                    'net': 8.05,
                    },
                {
                    'catalog_name': 'Akaline Kidal',
                    'version_number': 'SS-050lp',
                    'format': 'lp',
                    'quantity': 1,
                    'net': 8.05,
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




