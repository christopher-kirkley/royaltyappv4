import pytest
import json
import datetime
import time

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal, Bundle

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, process_pending_statements

from royaltyapp.income.util import pending_operations as po


def build_catalog(test_client, db):
    artist = Artist(
            artist_name='JoSchmo',
            prenom='Jo',
            surnom='Schmo'
            )
    db.session.add(artist)
    catalog_item = Catalog(
            catalog_number='TEST-01',
            catalog_name='test catalog',
            artist_id=1
            )
    db.session.add(catalog_item)
    version_item_1 = Version(
            version_number='TEST-01digi',
            upc='1',
            format='digital',
            catalog_id=1
            )
    db.session.add(version_item_1)
    version_item_2 = Version(
            version_number='TEST-01lp',
            upc='2',
            format='physical',
            catalog_id=1
            )
    db.session.add(version_item_2)
    version_item_3 = Version(
            version_number='TEST-01cass',
            upc='3',
            format='physical',
            catalog_id=1
            )
    db.session.add(version_item_3)
    bundle_item_1 = Bundle(
            bundle_number='BUNDLE-01',
            upc='4',
            )
    db.session.add(bundle_item_1)
    db.session.commit()
    bundle_version=[2, 3]
    obj=db.session.query(Bundle).get(bundle_item_1.id)
    for version in bundle_version:
        version_obj=db.session.query(Version).get(version)
        obj.version_bundle.append(version_obj)
    db.session.commit()

def add_income_pending(test_client, db, in_ver, in_upc):
    income = IncomePending(
            statement='teststatement',
            distributor='bandcamp',
            upc_id=in_upc,
            version_number=in_ver,
            )
    db.session.add(income)
    db.session.commit()

def test_build_catalog(test_client, db):
    build_catalog(test_client, db)
    assert len(db.session.query(Version).all())==3

def test_can_set_upc_on_version_number_match(test_client, db):
    build_catalog(test_client, db)
    in_ver='TEST-01lp'
    out_ver='TEST-01lp'
    in_upc=None
    out_upc=db.session.query(Version).filter(Version.version_number==out_ver).one().upc
    add_income_pending(test_client, db, in_ver, in_upc)
    po.add_missing_upc()    
    res = db.session.query(IncomePending).one()
    assert res.upc_id == out_upc

def test_can_set_upc_on_version_number_match_with_empty_upc(test_client, db):
    build_catalog(test_client, db)
    in_ver='TEST-01lp'
    out_ver='TEST-01lp'
    in_upc=''
    out_upc=db.session.query(Version).filter(Version.version_number==out_ver).one().upc
    add_income_pending(test_client, db, in_ver, in_upc)
    po.add_missing_upc()    
    res = db.session.query(IncomePending).one()
    assert res.upc_id == out_upc

def test_can_set_upc_on_version_number_cases(test_client, db):
    build_catalog(test_client, db)
    in_ver_list=[
            'TEST-01-lp',
            'TEST-01-LP',
            'TEST01LP',
            'TeSt01lP',
            'test01lp',
            ]
    out_ver='TEST-01lp'
    in_upc=None
    out_upc=db.session.query(Version).filter(Version.version_number==out_ver).one().upc
   
    for in_ver in in_ver_list:
        add_income_pending(test_client, db, in_ver, in_upc)
        id=db.session.query(IncomePending).filter(IncomePending.version_number==in_ver).one().id
        po.add_missing_upc()    
        res = db.session.query(IncomePending).filter(IncomePending.id==id).one()
        assert res.upc_id == out_upc

def test_can_set_upc_on_version_number_cases_and_empty_upc(test_client, db):
    build_catalog(test_client, db)
    in_ver_list=[
            'TEST-01-lp',
            'TEST-01-LP',
            'TEST01LP',
            'TeSt01lP',
            'test01lp',
            ]
    out_ver='TEST-01lp'
    in_upc=''
    out_upc=db.session.query(Version).filter(Version.version_number==out_ver).one().upc
   
    for in_ver in in_ver_list:
        add_income_pending(test_client, db, in_ver, in_upc)
        id=db.session.query(IncomePending).filter(IncomePending.version_number==in_ver).one().id
        po.add_missing_upc()    
        res = db.session.query(IncomePending).filter(IncomePending.id==id).one()
        assert res.upc_id == out_upc

def test_can_set_upc_on_bundle_number_cases(test_client, db):
    build_catalog(test_client, db)
    in_ver_list=[
            'BUNDLE-01',
            'BUNDLE-01-',
            'bundle-01',
            'BuNdLE01',
            ]
    out_ver='BUNDLE-01'
    in_upc=None
    out_upc=db.session.query(Bundle).filter(Bundle.bundle_number==out_ver).one().upc
   
    for in_ver in in_ver_list:
        add_income_pending(test_client, db, in_ver, in_upc)
        id=db.session.query(IncomePending).filter(IncomePending.version_number==in_ver).one().id
        po.add_missing_upc()    
        res = db.session.query(IncomePending).filter(IncomePending.id==id).one()
        assert res.upc_id == out_upc

def test_can_set_upc_on_bundle_number_cases_with_empty_upc(test_client, db):
    build_catalog(test_client, db)
    in_ver_list=[
            'BUNDLE-01',
            'BUNDLE-01-',
            'bundle-01',
            'BuNdLE01',
            ]
    out_ver='BUNDLE-01'
    in_upc=''
    out_upc=db.session.query(Bundle).filter(Bundle.bundle_number==out_ver).one().upc
   
    for in_ver in in_ver_list:
        add_income_pending(test_client, db, in_ver, in_upc)
        id=db.session.query(IncomePending).filter(IncomePending.version_number==in_ver).one().id
        po.add_missing_upc()    
        res = db.session.query(IncomePending).filter(IncomePending.id==id).one()
        assert res.upc_id == out_upc

def test_can_match_on_catalog_name_physical(test_client, db):
    build_catalog(test_client, db)

    in_catalog_name='TEST-01'
    in_upc=None
    out_upc=None

    income = IncomePending(
            statement='teststatement',
            distributor='bandcamp',
            upc_id=in_upc,
            album_name=in_catalog_name,
            medium='physical',
            type='album'
            )
    db.session.add(income)
    db.session.commit()
    
    po.match_upc_on_catalog_name()
    res = db.session.query(IncomePending).one()
    assert res.upc_id == out_upc

def test_can_match_on_catalog_name_digital(test_client, db):
    build_catalog(test_client, db)

    in_catalog_name='test catalog'
    in_upc=None
    out_upc='1'

    income = IncomePending(
            statement='teststatement',
            distributor='bandcamp',
            upc_id=in_upc,
            album_name=in_catalog_name,
            medium='digital',
            type='album'
            )
    db.session.add(income)
    db.session.commit()
    
    po.match_upc_on_catalog_name()
    res = db.session.query(IncomePending).one()
    assert res.upc_id == out_upc

def test_can_add_missing_version_number(test_client, db):
    build_catalog(test_client, db)
    add_income_pending(test_client, db, '', '1')
    res = db.session.query(IncomePending).one()
    assert res.version_number == ''
    assert res.upc_id == '1'
    po.add_missing_version_number()
    res = db.session.query(IncomePending).one()
    assert res.upc_id == '1'
    assert res.version_number == 'TEST-01digi'

