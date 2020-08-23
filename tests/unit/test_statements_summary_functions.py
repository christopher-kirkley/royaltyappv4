import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from decimal import Decimal

import time

from royaltyapp.models import StatementGenerated, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending


from royaltyapp.statements.util import generate_artist_statement as ga

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement, setup_test1, setup_statement


def test_can_find_statement_table(test_client, db):
    setup_statement(test_client, db)
    table = ga.get_statement_table(1)
    assert table.name == 'statement_2020_01_01_2020_01_31'

def test_can_get_statement_previous_balance_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    assert db.session.query(statement_previous_balance_by_artist).all() == []

def test_can_get_statement_sales_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    assert db.session.query(statement_sales_by_artist).all() == [(1, Decimal('24.95'))]

def test_can_get_statement_advances_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    assert db.session.query(statement_advances_by_artist).all() == [
            (1, Decimal('9542.63')),
            (None, Decimal('1078.46'))
            ]

def test_can_get_statement_recoupables_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    assert db.session.query(statement_recoupables_by_artist).all() == [
            (1, Decimal('1398.06')),
            ]

def test_can_create_statement_summary_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ga.create_statement_summary_table(date_range)
    assert len(db.session.query(table).all()) == 0
    assert table.__tablename__ == 'statement_summary_2020_01_01_2020_01_31'

def test_can_get_statement_by_artist_subquery(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': None,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    date_range = '2020_01_01_2020_01_31'
    statement_by_artist = ga.create_statement_by_artist_subquery(
                                                        statement_previous_balance_by_artist,
                                                        statement_sales_by_artist,
                                                        statement_advances_by_artist,
                                                        statement_recoupables_by_artist)
    assert len((statement_by_artist).all()) > 0
    assert statement_by_artist.all() == [
            (
                1, # artist_id
                Decimal('0'), # previous_balance 
                Decimal('1398.06'), # recoupable
                Decimal('24.95'), # sales 
                Decimal('9542.63'), # advance
                )]

def test_can_insert_statement_summary_data_into_table(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    date_range = '2020_01_01_2020_01_31'
    table = ga.create_statement_summary_table(date_range)
    statement_summary_table = table.__table__
    statement_by_artist = ga.create_statement_by_artist_subquery(
                                                        statement_previous_balance_by_artist,
                                                        statement_sales_by_artist,
                                                        statement_advances_by_artist,
                                                        statement_recoupables_by_artist)
    ga.insert_into_statement_summary(statement_by_artist, statement_summary_table)
    assert len(db.session.query(table).all()) > 0
    res = db.session.query(table).first()
    assert res.id == 1
    assert res.artist_id == 1
    assert res.previous_balance == Decimal('0')
    assert res.recoupables == Decimal('1398.06')
    assert res.advances == Decimal('9542.63')
    assert res.sales == Decimal('24.95')

def test_can_link_previous_balance(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': None,
            'start_date': '2020-01-01',
            'end_date': '2020-01-15'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    response = test_client.post('/statements/1/generate-summary')
    assert response.status_code == 200

    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-16',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    response = test_client.post('/statements/2/generate-summary')
    assert response.status_code == 200

    res = db.session.query(StatementGenerated)
    assert len(res.all()) == 2
    assert res.all()[0].previous_balance_id == None
    assert res.all()[1].previous_balance_id == 1

    metadata = db.MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_01_2020_01_15_balance')
    res = db.session.query(table).all()
    assert len(res) == 1
    res = db.session.query(table).first()
    assert res.balance_forward == Decimal('-10216.71')
    
    metadata = db.MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_16_2020_01_31')
    res = db.session.query(table).all()
    assert len(res) == 0
    table = metadata.tables.get('statement_summary_2020_01_16_2020_01_31')
    res = db.session.query(table).first()
    assert res.previous_balance == Decimal('-10216.71')


