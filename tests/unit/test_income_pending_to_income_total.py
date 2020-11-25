import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

import time

from sqlalchemy import func

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, IncomeTotal

from royaltyapp.income.util import process_income as pi

from .helpers import post_data, build_catalog, add_bandcamp_sales, add_bandcamp_order_settings, add_two_bandcamp_sales, add_test1_bandcamp_sales

cases = {
        'case_1': (
            { 
                'bandcamp': [
                    'import_bandcamp.csv'
                    ]
                },
            {'records': 732, 'amount_total': 4626.58}
            ),
        'case_2': (
            { 
                'shopify': [
                    'import_shopify.csv',
                    ]
                },
            {'records': 4, 'amount_total': 57.0}),
        'case_3': (
            { 
                'sddigital': [
                    'import_sddigital.csv',
                    ]
                },
            {'records': 13, 'amount_total': 7.53}),
        'case_4': (
            { 
                'sdphysical': [
                    'import_sdphysical.csv',
                    ]
                },
            {'records': 43, 'amount_total': 35.32}),
        'case_5': (
            { 
                'quickbooks': [
                    'import_quickbooks.csv',
                    ]
                },
            {'records': 2, 'amount_total': 1229.00}),
        'case_6': (
            { 
                'sds': [
                    'import_sds.csv',
                    ]
                },
            {'records': 10, 'amount_total': 0.05}),
        }

order_fee_cases = {
        'case_1': (
            { 
                'bandcamp': [
                    'import_bandcamp_3.csv'
                    ]
                },
            {   
                'records': 16,
                'amount_total': 128.56,
                'label_fee_total': 8.63,
                'label_net_total': 119.93
                }
            ),
        }

@pytest.mark.parametrize('statements, expected', list(cases.values()), ids=list(cases.keys()))
def test_can_normalize_distributor(test_client, db, statements, expected):
    build_catalog(db, test_client)
    for statement_type, filelist in statements.items():
        for _file in filelist:
            post_data(test_client, _file, statement_type)
    distributors = db.session.query(IncomePending.distributor).distinct().all()
    for distributor in distributors:
        income_distributor_id = (db.session.query(IncomePending)
                .filter(IncomePending.distributor == distributor)
                ).first().distributor_id
        assert income_distributor_id == None
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
    assert res.start_date.strftime("%Y-%m-%d") == '2020-01-01'
    assert res.end_date.strftime("%Y-%m-%d") == '2020-01-04'

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

@pytest.mark.parametrize('statements, expected', list(cases.values()), ids=list(cases.keys()))
def test_can_insert_into_total_no_order_fee(test_client, db, statements, expected):
    build_catalog(db, test_client)
    for statement_type, filelist in statements.items():
        for _file in filelist:
            post_data(test_client, _file, statement_type)
    res = db.session.query(IncomePending).all()
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.normalize_statement_id()
    pi.calculate_adjusted_amount()
    pi.move_from_pending_income_to_total()
    assert len(db.session.query(IncomeTotal).all()) == expected['records']
    total_amount = (db.session
            .query(func.sum(IncomeTotal.amount))
            .one()[0])
    assert round(float(total_amount), 2) == expected['amount_total']

@pytest.mark.parametrize('statements, expected', list(order_fee_cases.values()), ids=list(order_fee_cases.keys()))
def test_can_insert_into_total_order_fee(test_client, db, statements, expected):
    build_catalog(db, test_client)
    add_bandcamp_order_settings(db)
    for statement_type, filelist in statements.items():
        for _file in filelist:
            post_data(test_client, _file, statement_type)
    res = db.session.query(IncomePending).all()
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.normalize_statement_id()
    pi.calculate_adjusted_amount()
    pi.move_from_pending_income_to_total()
    assert len(db.session.query(IncomeTotal).all()) == expected['records']
    amount_total = (db.session
            .query(func.sum(IncomeTotal.amount))
            .one()[0])
    assert round(float(amount_total), 2) == expected['amount_total']
    label_fee_total = (db.session
            .query(func.sum(IncomeTotal.label_fee))
            .one()[0])
    assert round(float(label_fee_total), 2) == expected['label_fee_total']
    label_net_total = (db.session
            .query(func.sum(IncomeTotal.label_net))
            .one()[0])
    assert round(float(label_net_total), 2) == expected['label_net_total']
