import os
import pandas as pd
import numpy as np
import json

from royaltyapp.models import Artist, Catalog, Version, Track, OrderSettings

from royaltyapp.catalog.helpers import clean_catalog_df, clean_track_df

from royaltyapp.income.util import process_income as pi

from royaltyapp.expense.util import process_expense as pe


def post_data(test_client, filename, import_type):
    path = os.getcwd() + '/tests/files/' + filename
    data = {
            'statement_source': import_type
            }
    data['file'] = (path, filename)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def add_one_artist(db):
    new_artist = Artist(artist_name='Amanar',
                        prenom='Ahmed',
                        surnom='Ag Kaedi',
                        )
    db.session.add(new_artist)
    db.session.commit()

def add_second_artist(db):
    new_artist = Artist(artist_name='Bobo',
                        prenom='Bob',
                        surnom='Jones',
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

def add_two_version(db):
    add_one_catalog(db)
    new_version = Version(
                        upc='123456',
                        version_number='SS-001lp',
                        version_name='Limited Vinyl',
                        format='LP',
                        catalog_id=1
                        )
    db.session.add(new_version)
    new_version = Version(
                        upc='78910',
                        version_number='SS-001cd',
                        version_name='Compact Disk',
                        format='CD',
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

def make_pending_catalog(db):
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    df = pd.read_csv(path)
    df = clean_catalog_df(df)
    df.to_sql('pending_catalog', con=db.engine, if_exists='append', index_label='id')
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

def add_bandcamp_errors(test_client):
    path = os.getcwd() + "/tests/files/test_bandcamp_errors.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'test_bandcamp_errors.csv')
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
    
def add_test1_bandcamp_sales(test_client):
    path = os.getcwd() + "/tests/files/test1_bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'test1_bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

def add_bandcamp_order_settings(db):
    order_setting_id = (db.session.query(OrderSettings)
            .filter(OrderSettings.distributor_id == 1)
            ).one().id
    obj = db.session.query(OrderSettings).get(order_setting_id)
    obj.order_percentage = 0.01
    obj.order_fee = 2.00
    obj.order_limit = 5.00
    db.session.commit()
    return True

def add_artist_expense(test_client): 
    path = os.getcwd() + "/tests/files/test1_expense_artist.csv"
    data = {
            'file': (path, 'expense_artist.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")

def add_artist_expense_two(test_client): 
    path = os.getcwd() + "/tests/files/test2_expense_artist.csv"
    data = {
            'file': (path, 'expense_artist_2.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")

def add_catalog_expense(test_client): 
    path = os.getcwd() + "/tests/files/expense_catalog.csv"
    data = {
            'file': (path, 'expense_catalog.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")

def add_type_expense(test_client): 
    path = os.getcwd() + "/tests/files/expense_type.csv"
    data = {
            'file': (path, 'expense_type.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")

def add_processed_income(test_client, db):
    add_bandcamp_sales(test_client)
    add_order_settings(db)
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.normalize_statement_id()
    pi.move_from_pending_income_to_total()

def add_processed_expense(test_client, db):
    add_artist_expense(test_client)

def generate_statement(test_client):
    date_range = '2020_01_01_2020_01_31'
    data = {
            'previous_balance_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)

def setup_test1(test_client, db):
    path = os.getcwd() + "/tests/files/test1_catalog.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    path = os.getcwd() + "/tests/files/test1_track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    path = os.getcwd() + "/tests/files/test1_version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    path = os.getcwd() + "/tests/files/test1_bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'test1_bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    add_order_settings(db)
    path = os.getcwd() + "/tests/files/test1_expense_artist.csv"
    data = {
            'file': (path, 'test1_expense_artist.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")
    path = os.getcwd() + "/tests/files/test1_expense_catalog.csv"
    data = {
            'file': (path, 'test1_expense_catalog.csv')
            }
    response = test_client.post('/expense/import-statement',
            data=data, content_type="multipart/form-data")
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.normalize_statement_id()
    pi.calculate_adjusted_amount()
    pi.move_from_pending_income_to_total()
    pe.normalize_artist()
    pe.normalize_catalog()
    pe.normalize_expense_type()
    pe.insert_into_imported_statements()
    pe.normalize_statement_id()
    pe.move_from_pending_expense_to_total()

def setup_statement(test_client, db):
    setup_test1(test_client, db)
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    response = test_client.post('/statements/1/generate-summary', data=json_data)

def add_one_bundle(test_client, db):
    add_one_catalog(db)
    add_two_version(db)
    data = {'bundle_number': 'SS-TESTBUNDLE',
            'bundle_name': 'Two Versions',
            'upc': '999111',
            'bundle_version': [
                {
                    'version_id': '1'
                    },
                {
                    'version_id': '2'
                    },
                ]
            }
    json_data = json.dumps(data)
    response = test_client.post('/bundle', data=json_data)

