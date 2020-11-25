import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

import time

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, IncomeTotal, ExpensePending, ExpenseType, ExpenseTotal

from royaltyapp.expense.util import process_expense as pe

from .helpers import build_catalog, add_artist_expense, add_catalog_expense, add_type_expense

def test_can_normalize_artist(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    res = db.session.query(ExpensePending).first()
    assert res.artist_name == 'Ahmed Ag Kaedy'
    new_artist = db.session.query(Artist).filter(Artist.artist_name == 'Ahmed Ag Kaedy').first().id
    pe.normalize_artist()
    res = db.session.query(ExpensePending).filter(ExpensePending.artist_id == '1').first()
    assert res.artist_id == new_artist

def test_can_normalize_catalog(test_client, db):
    build_catalog(db, test_client)
    add_catalog_expense(test_client)
    res = db.session.query(ExpensePending).filter(ExpensePending.catalog_number == 'SS-050').first()
    assert res.catalog_number == 'SS-050'
    new_catalog_id = db.session.query(Catalog).filter(Catalog.catalog_number == 'SS-050').first().id
    assert new_catalog_id == 1
    pe.normalize_catalog()
    res = db.session.query(ExpensePending).filter(ExpensePending.catalog_number == 'SS-050').first()
    assert res.catalog_id == new_catalog_id

def test_can_normalize_expense_type(test_client, db):
    build_catalog(db, test_client)
    add_type_expense(test_client)
    res = db.session.query(ExpensePending).filter(ExpensePending.expense_type == 'Advance').first()
    assert res.expense_type == 'Advance'
    new_expense_type = db.session.query(ExpenseType).filter(ExpenseType.expense_type == 'advance').first().id
    assert new_expense_type == 1
    pe.normalize_expense_type()
    res = db.session.query(ExpensePending).filter(ExpensePending.expense_type == 'Advance').first()
    assert res.expense_type_id == new_expense_type

def test_can_insert_into_imported_statements_table(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    pe.normalize_artist()
    pe.normalize_catalog()
    pe.normalize_expense_type()
    assert pe.insert_into_imported_statements() == True
    query = db.session.query(ImportedStatement).all()
    assert len(query) != 0
    res = db.session.query(ImportedStatement).first()
    assert res.statement_name == 'expense_artist.csv'
    assert res.transaction_type == 'expense'
    assert res.start_date.strftime("%Y-%m-%d") == '2020-01-01'
    assert res.end_date.strftime("%Y-%m-%d") == '2020-01-01'

def test_can_normalize_statement_id(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    pe.normalize_artist()
    pe.normalize_catalog()
    pe.normalize_expense_type()
    pe.insert_into_imported_statements()
    assert pe.normalize_statement_id() == True
    new_statement_id = db.session.query(ImportedStatement).first().id
    res = db.session.query(ExpensePending).first()
    assert res.imported_statement_id == new_statement_id

def test_can_insert_into_total(test_client, db):
    build_catalog(db, test_client)
    add_artist_expense(test_client)
    pe.normalize_artist()
    pe.normalize_catalog()
    pe.normalize_expense_type()
    pe.insert_into_imported_statements()
    pe.normalize_statement_id()
    pe.move_from_pending_expense_to_total()    
    res = db.session.query(ExpenseTotal).all()
    assert len(res) == 4
