import pytest
import json

import os
import io

import pandas as pd

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion
from .helpers import add_one_artist, add_one_catalog, add_one_version, add_one_track, make_pending, make_pending_version

from royaltyapp.catalog.helpers import clean_df, pending_to_artist, pending_to_catalog, pending_version_to_version

def test_can_import_catalog(test_client, db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    query = db.session.query(Pending).all()
    assert len(query) != 0
    query = db.session.query(Pending).first()
    assert query.track_artist == 'Ahmed Ag Kaedy'
    query = db.session.query(Artist).first()
    assert query.artist_name == 'Ahmed Ag Kaedy'
    query = db.session.query(Catalog).first()
    assert query.catalog_name == 'Akaline Kidal'

def test_can_clean_csv(test_client):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    df = pd.read_csv(path)
    assert len(df) != 0
    df = clean_df(df)
    assert df['track_artist'][0] == "Ahmed Ag Kaedy"
    # write some tests for edge cases here

def test_can_load_database(db):
    query = db.session.query(Pending).all()
    assert len(query) == 0

def test_can_process_df(db):
    make_pending(db)
    query = db.session.query(Pending).all()
    assert len(query) != 0
    pending_to_artist(db)
    query = db.session.query(Artist).all()
    assert len(query) == 3
    assert query[0].artist_name == 'Ahmed Ag Kaedy'
    assert query[2].artist_name == 'Various Artist'
    pending_to_catalog(db)
    query = db.session.query(Catalog).all()
    assert len(query) == 2
    assert query[0].catalog_name == 'Akaline Kidal'
    
def test_can_import_version(test_client, db):
    make_pending(db)
    pending_to_artist(db)
    pending_to_catalog(db)
    path = os.getcwd() + "/tests/files/one_version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    query = db.session.query(PendingVersion).all()
    assert len(query) != 0
    query = db.session.query(PendingVersion).first()
    assert query.version_number == 'SS-050cass'
    query = db.session.query(Catalog).first()
    assert len(query.version) == 3

