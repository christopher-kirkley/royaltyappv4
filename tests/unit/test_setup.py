import pytest
import json

import os
import pandas as pd

from royaltyapp.models import Artist, Catalog, Version, Track, Pending
from .helpers import add_one_artist, add_one_catalog, add_one_version, add_one_track

from royaltyapp.catalog.helpers import clean_df

def test_can_import_catalog(test_client, db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    data = {
            'body': path
            }
    json_data = json.dumps(data)
    response = test_client.post('/catalog/import-catalog', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    query = db.session.query(Pending).all()
    assert len(query) != 0
    query = db.session.query(Pending).first()
    assert query.track_artist == 'Ahmed Ag Kaedy'
    
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
