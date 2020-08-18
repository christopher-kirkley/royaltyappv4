import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

import time

from royaltyapp.models import StatementGenerated, StatementBalanceGenerated, StatementBalance, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending

from royaltyapp.statements.helpers import define_artist_statement_table

from royaltyapp.statements.util import generate_statement as ge
from royaltyapp.statements.util import generate_artist_statement as ga

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement, setup_test1


def test_can_list_statements(test_client, db):
    build_catalog(db, test_client)
    add_processed_income(test_client, db)
    add_processed_expense(test_client, db)
    response = test_client.get('/statements/view-balances')
    assert response.status_code == 200
    assert json.loads(response.data) == [{
        'id': 1,
        'statement_balance_name': 'none_balance'
        }]

def test_can_generate_statement(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31',
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'True',
                                        'statement_index': 1}
    res = db.session.query(StatementGenerated).all()
    assert len(res) == 1
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 2
    res = db.session.query(StatementBalance).all()
    assert len(res) == 1
    metadata = db.MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_01_2020_01_31')
    res = db.session.query(table).all()
    assert len(res) != 0
    
def test_can_create_new_statement_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    assert table.__tablename__ == 'statement_2020_01_01_2020_01_31'

def test_can_add_statement_to_index(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_generated = ge.add_statement_to_index(table, statement_summary_table)
    assert statement_generated.id == 1
    res = db.session.query(StatementGenerated).all()
    assert len(res) == 1

def test_can_create_new_statement_balance_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_generated = ge.add_statement_to_index(table, statement_summary_table)
    assert statement_generated.id == 1
    statement_balance_table = ge.create_statement_balance_table(table)
    assert statement_balance_table.__tablename__ == 'statement_2020_01_01_2020_01_31_balance'

def test_can_add_statement_balance_to_index(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_generated = ge.add_statement_to_index(table, statement_summary_table)
    assert statement_generated.id == 1
    statement_balance_table = ge.create_statement_balance_table(table)
    assert statement_balance_table.__tablename__ == 'statement_2020_01_01_2020_01_31_balance'
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 1

    statement_balance_generated = ge.add_statement_balance_to_index(statement_balance_table)
    assert statement_balance_generated.id == 2
    res = db.session.query(StatementBalanceGenerated).all()
    assert len(res) == 2
    
def test_can_populate_relationship_table(test_client, db):
    date_range = '2020_01_01_2020_01_31'
    table = ge.create_statement_table(date_range)
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_index = ge.add_statement_to_index(table, statement_summary_table)
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
        'statement_detail_table': 'statement_2020_01_01_2020_01_31',
        'statement_summary_table': 'statement_summary_2020_01_01_2020_01_31'
        }]


def test_can_find_track_percentage(test_client, db):
    setup_test1(test_client, db)
    assert len(db.session.query(Version).all()) > 0
    assert len(db.session.query(Catalog).all()) > 0
    assert len(db.session.query(Track).all()) > 0
    assert len(db.session.query(TrackCatalogTable).all()) > 0
    assert len(db.session.query(IncomeTotal).all()) > 0
    artist_catalog_percentage = ge.find_track_percentage()
    assert len(db.session.query(artist_catalog_percentage).all()) == 1

def test_can_find_artist_total(test_client, db):
    start_date = '2020-01-01'
    end_date = '2020-01-31'
    setup_test1(test_client, db)
    artist_catalog_percentage = ge.find_track_percentage()
    artist_total = ge.find_artist_total(start_date, end_date, artist_catalog_percentage)
    assert len(artist_total.all()) > 0

def test_setup_test(test_client, db):
    assert db.session.query(IncomePending).all() == []
    setup_test1(test_client, db)
    assert len(db.session.query(IncomeTotal).all()) > 0

def test_can_insert_income_into_table(test_client, db):
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
    metadata = db.MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_01_2020_01_31')
    artist_catalog_percentage = ge.find_track_percentage()
    artist_total = ge.find_artist_total(start_date, end_date, artist_catalog_percentage)
    ge.insert_into_table(artist_total, table)
    res = db.session.query(table).all()
    assert len(res) != 0

def test_can_find_expense_total(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    previous_balance_id = data['previous_balance_id']
    date_range = (str(start_date) + '_' + str(end_date)).replace('-', '_')
    table = ge.create_statement_table(date_range)
    table_obj = table.__table__
    artist_catalog_percentage = ge.find_track_percentage()
    metadata = db.MetaData(db.engine, reflect=True)
    table = metadata.tables.get('statement_2020_01_01_2020_01_31')
    artist_catalog_percentage = ge.find_track_percentage()
    expense_total = ge.find_expense_total(start_date, end_date, artist_catalog_percentage)
    assert len(expense_total.all()) > 0
    ge.insert_expense_into_total(expense_total, table_obj)
    advances = db.session.query(table).filter(table.c.expense_type_id == 1).all()
    recoupables = db.session.query(table).filter(table.c.expense_type_id == 2).all()
    assert len(advances) == 5
    assert len(recoupables) == 1

