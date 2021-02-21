import pytest
import json
import datetime
import time
from decimal import Decimal

import os
import io

import pandas as pd
import numpy as np

from sqlalchemy import func

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal, Bundle

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, process_pending_statements

from .helpers import post_data, add_bandcamp_sales, add_bandcamp_order_settings, add_artist_expense, add_bandcamp_errors, add_two_bandcamp_sales

from royaltyapp.income.util import process_income as pi

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

def add_income_pending(test_client, db):
    income = IncomePending(
            statement='teststatement',
            distributor='bandcamp',
            upc_id='4',
            )
    db.session.add(income)
    db.session.commit()

def test_can_split_bundle(test_client, db):
    build_catalog(test_client, db)
    add_income_pending(test_client, db)
    query = db.session.query(IncomePending).all()
    assert len(query) == 1
    pi.split_bundle_into_versions()
    query = db.session.query(IncomePending).all()
    assert len(query) == 2
    assert query[0].version_id == 2
    assert query[1].version_id == 3

