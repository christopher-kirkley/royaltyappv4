import pytest
import json

import os
import io

import pandas as pd

import time

from royaltyapp.models import Artist, Catalog, Version, Track, PendingCatalog, PendingTrack, PendingVersion, IncomeDistributor

from .helpers import add_one_artist, add_one_catalog, add_one_version, add_one_track, make_pending_catalog, make_pending_version

from royaltyapp.catalog.helpers import clean_catalog_df, clean_track_df, pending_catalog_to_artist, pending_catalog_to_catalog, pending_version_to_version

from royaltyapp.models import insert_initial_values

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
    query = db.session.query(PendingCatalog).all()
    assert len(query) != 0
    query = db.session.query(PendingCatalog).first()
    assert query.catalog_number == 'SS-050'
    query = db.session.query(Artist).all()
    assert query[0].artist_name == 'Various Artist'
    assert query[1].artist_name == 'Ahmed Ag Kaedy'
    query = db.session.query(Catalog).all()
    assert len(query) == 2
    assert query[0].catalog_name == 'Akaline Kidal'
    assert query[1].catalog_name == 'Compilation'

def test_can_import_tracks(test_client, db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + "/tests/files/one_track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    query = db.session.query(PendingTrack).all()
    assert len(query) != 0
    query = db.session.query(PendingTrack).all()
    assert query[0].track_artist == 'Ahmed Ag Kaedy'
    assert query[0].track_number == 1
    assert query[0].isrc == 'QZDZE1905001'
    assert query[0].catalog_number == 'SS-050'
    assert query[1].track_artist == 'Ahmed Ag Kaedy'
    assert query[1].track_number == 2
    assert query[1].isrc == 'QZDZE1905002'
    query = db.session.query(Catalog).first()
    assert query.catalog_name == 'Akaline Kidal'
    assert len(db.session.query(Artist).all()) == 3
    artists = db.session.query(Artist).all()
    assert artists[0].artist_name == 'Various Artist'
    assert artists[1].artist_name == 'Ahmed Ag Kaedy'
    assert artists[2].artist_name == 'Bonehead Jones'
    query = db.session.query(Track).all()
    assert len(query) == 13

def test_can_import_version(test_client, db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
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

def test_can_clean_catalog_csv(test_client):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    df = pd.read_csv(path)
    assert len(df) != 0
    df = clean_catalog_df(df)
    assert df['catalog_artist'][0] == "Ahmed Ag Kaedy"
    # write some tests for edge cases here

def test_can_load_database(db):
    query = db.session.query(PendingCatalog).all()
    assert len(query) == 0
    query = db.session.query(PendingTrack).all()
    assert len(query) == 0
    query = db.session.query(PendingVersion).all()
    assert len(query) == 0

def test_can_process_df(db):
    make_pending_catalog(db)
    query = db.session.query(PendingCatalog).all()
    assert len(query) != 0
    pending_catalog_to_artist(db)
    query = db.session.query(Artist).all()
    assert len(query) == 2
    assert query[0].artist_name == 'Various Artist'
    assert query[1].artist_name == 'Ahmed Ag Kaedy'
    pending_catalog_to_catalog(db)
    query = db.session.query(Catalog).all()
    assert len(query) == 2
    assert query[0].catalog_name == 'Akaline Kidal'
    
def test_can_make_track_df(test_client, db):
    path = os.getcwd() + "/tests/files/one_track.csv"
    df = pd.read_csv(path)
    df = clean_track_df(df)
    assert len(df) == 13





