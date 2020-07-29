import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, IncomeTotal

from royaltyapp.income.util import process_income as pi

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_two_bandcamp_sales

def test_can_normalize_distributor(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    res = db.session.query(IncomePending).first()
    assert res.distributor == 'bandcamp'
    query = db.session.query(IncomeDistributor).all()
    assert len(query) != 0
    pi.normalize_distributor()
    res = db.session.query(IncomePending).first()
    assert res.distributor_id == 1

def test_can_normalize_version(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    res = db.session.query(IncomePending).first()
    assert res.upc_id == '602318136817'
    new_version = db.session.query(Version).filter(Version.upc == '602318136817').first().id
    pi.normalize_version()
    res = db.session.query(IncomePending).filter(IncomePending.upc_id == '602318136817').first()
    assert res.version_id == new_version

def test_can_normalize_track(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    res = db.session.query(IncomePending).filter(IncomePending.isrc_id == 'QZDZE1905001').first()
    assert res.isrc_id == 'QZDZE1905001'
    new_track_id = db.session.query(Track).filter(Track.isrc == 'QZDZE1905001').first().id
    pi.normalize_track()
    res = db.session.query(IncomePending).filter(IncomePending.isrc_id == 'QZDZE1905001').first()
    assert res.track_id == new_track_id

def test_can_insert_into_imported_statements_table(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    assert pi.insert_into_imported_statements() == True
    query = db.session.query(ImportedStatement).all()
    assert len(query) != 0
    res = db.session.query(ImportedStatement).first()
    assert res.statement_name == 'one_bandcamp_test.csv'
    assert res.transaction_type == 'income'
    assert res.income_distributor_id == 1

def test_can_normalize_statement_id(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    assert pi.normalize_statement_id() == True
    new_statement_id = db.session.query(ImportedStatement).first().id
    res = db.session.query(IncomePending).first()
    assert res.statement_id == new_statement_id

def test_can_calculate_adjusted_label_amount(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    assert pi.calculate_adjusted_amount() == True
    res = db.session.query(IncomePending).filter(IncomePending.id == 4).first()
    assert res.id == 4
    assert res.label_fee == 0
    assert float(res.label_net) == 6.26
    add_order_settings(db)
    assert pi.calculate_adjusted_amount() == True
    res = db.session.query(IncomePending).filter(IncomePending.id == 4).first()
    assert res.id == 4
    assert float(res.label_fee) == 2.06
    assert float(res.label_net) == 4.20

def test_can_divide_fees_over_order_items(test_client, db):
    build_catalog(db, test_client)
    add_two_bandcamp_sales(test_client)
    res = db.session.query(IncomePending).all()
    assert len(res) != 0
    add_order_settings(db)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    assert pi.calculate_adjusted_amount() == True
    res = db.session.query(IncomePending).first()
    assert float(res.label_fee) == 0.73
    assert float(res.label_net) == 5.53

def test_zero_out_label_fees(test_client, db):
    build_catalog(db, test_client)
    add_two_bandcamp_sales(test_client)
    add_order_settings(db)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    assert pi.calculate_adjusted_amount() == True
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '2').first()
    assert res.label_fee == 0
    res = db.session.query(IncomePending).filter(IncomePending.order_id == '3').first()
    assert res.label_fee == 0

def test_can_insert_into_total(test_client, db):
    build_catalog(db, test_client)
    add_two_bandcamp_sales(test_client)
    res = db.session.query(IncomePending).all()
    add_order_settings(db)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.move_from_pending_income_to_total()
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 5    
