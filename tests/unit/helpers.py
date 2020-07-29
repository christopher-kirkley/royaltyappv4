import os
import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, OrderSettings

from royaltyapp.catalog.helpers import clean_df


def add_one_artist(db):
    new_artist = Artist(artist_name='Amanar',
                        prenom='Ahmed',
                        surnom='Ag Kaedi',
                        )
    db.session.add(new_artist)
    db.session.commit()

def add_one_catalog(db):
    add_one_artist(db)
    new_catalog = Catalog(catalog_number='SS-001',
                        catalog_name='Ishilan N-Tenere',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()

def add_one_version(db):
    add_one_catalog(db)
    new_version = Version(
                        upc='123456',
                        version_number='SS-001lp',
                        version_name='Limited Vinyl',
                        format='LP',
                        catalog_id=1
                        )
    db.session.add(new_version)
    db.session.commit()

def add_one_track(db):
    add_one_catalog(db)
    obj = db.session.query(Catalog).first()
    new_track = Track(
                    track_number='1',
                    track_name='Potatoes for Sale',
                    isrc='abc123',
                    artist_id='1'
                    )
    obj.tracks.append(new_track)
    db.session.commit()

def make_pending(db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    df = pd.read_csv(path)
    df = clean_df(df)
    df.to_sql('pending', con=db.engine, if_exists='append', index_label='id')
    return True

def make_pending_version(db):
    path = os.getcwd() + "/tests/files/one_version.csv"
    df = pd.read_csv(path)
    df.to_sql('pending_version', con=db.engine, if_exists='append', index_label='id')
    return True

def build_catalog(db, test_client):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    path = os.getcwd() + "/tests/files/one_version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)

def add_bandcamp_sales(test_client):
    path = os.getcwd() + "/tests/files/one_bandcamp_test.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'one_bandcamp_test.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

def add_two_bandcamp_sales(test_client):
    path = os.getcwd() + "/tests/files/two_bandcamp_test.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'two_bandcamp_test.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

def add_order_settings(db):
    new_order_setting = OrderSettings(
                    distributor_id = 1,
                    order_percentage = 0.01,
                    order_fee = 2.00
                    )
    db.session.add(new_order_setting)
    db.session.commit()


