import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, IncomeTotal, ExpensePending, ExpenseType

from royaltyapp.expense.util import process_expense as pe

from .helpers import build_catalog, add_artist_expense, add_catalog_expense, add_type_expense

# def test_can_normalize_distributor(test_client, db):
#     build_catalog(db, test_client)
#     add_artist_expense(test_client)
#     add_catalog_expense(test_client)
#     res = db.session.query(ExpensePending).all()
#     assert len(res) == 8
    # query = db.session.query(IncomeDistributor).all()
    # assert len(query) != 0
    # pi.normalize_distributor()
    # res = db.session.query(IncomePending).first()
    # assert res.distributor_id == 1

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

# def test_can_normalize_statement_id(test_client, db):
    # build_catalog(db, test_client)
    # add_bandcamp_sales(test_client)
    # pi.normalize_distributor()
    # pi.normalize_version()
    # pi.normalize_track()
    # pi.insert_into_imported_statements()
    # assert pi.normalize_statement_id() == True
    # new_statement_id = db.session.query(ImportedStatement).first().id
    # res = db.session.query(IncomePending).first()
    # assert res.statement_id == new_statement_id

# def test_can_calculate_adjusted_label_amount(test_client, db):
    # build_catalog(db, test_client)
    # add_bandcamp_sales(test_client)
    # pi.normalize_distributor()
    # pi.normalize_version()
    # pi.normalize_track()
    # pi.insert_into_imported_statements()
    # assert pi.calculate_adjusted_amount() == True
    # res = db.session.query(IncomePending).filter(IncomePending.id == 4).first()
    # assert res.id == 4
    # assert res.label_fee == 0
    # assert float(res.label_net) == 6.26
    # add_order_settings(db)
    # assert pi.calculate_adjusted_amount() == True
    # res = db.session.query(IncomePending).filter(IncomePending.id == 4).first()
    # assert res.id == 4
    # assert float(res.label_fee) == 2.06
    # assert float(res.label_net) == 4.20

# def test_can_divide_fees_over_order_items(test_client, db):
    # build_catalog(db, test_client)
    # add_two_bandcamp_sales(test_client)
    # res = db.session.query(IncomePending).all()
    # assert len(res) != 0
    # add_order_settings(db)
    # pi.normalize_distributor()
    # pi.normalize_version()
    # pi.normalize_track()
    # pi.insert_into_imported_statements()
    # assert pi.calculate_adjusted_amount() == True
    # res = db.session.query(IncomePending).first()
    # assert float(res.label_fee) == 0.73
    # assert float(res.label_net) == 5.53

# def test_zero_out_label_fees(test_client, db):
    # build_catalog(db, test_client)
    # add_two_bandcamp_sales(test_client)
    # add_order_settings(db)
    # pi.normalize_distributor()
    # pi.normalize_version()
    # pi.normalize_track()
    # pi.insert_into_imported_statements()
    # assert pi.calculate_adjusted_amount() == True
    # res = db.session.query(IncomePending).filter(IncomePending.order_id == '2').first()
    # assert res.label_fee == 0
    # res = db.session.query(IncomePending).filter(IncomePending.order_id == '3').first()
    # assert res.label_fee == 0

# def test_can_insert_into_total(test_client, db):
    # build_catalog(db, test_client)
    # add_two_bandcamp_sales(test_client)
    # res = db.session.query(IncomePending).all()
    # add_order_settings(db)
    # pi.normalize_distributor()
    # pi.normalize_version()
    # pi.normalize_track()
    # pi.insert_into_imported_statements()
    # pi.normalize_statement_id()
    # pi.move_from_pending_income_to_total()
    # res = db.session.query(IncomeTotal).all()
    # assert len(res) == 5    
    # res = db.session.query(IncomeTotal).first()
    # assert res.id == 1
    # assert res.income_distributor_id == 1
    # assert res.imported_statement_id == 1
