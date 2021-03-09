import os
import pytest

import datetime
import json

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle, BundleVersionTable, PendingBundle

from sqlalchemy import func, MetaData

from decimal import Decimal

import time

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def import_catalog(test_client, db, case):
    path = os.getcwd() + f'/tests/api/{case}/catalog.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/api/{case}/version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/api/{case}/track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    assert response.status_code == 200

def import_bundle(test_client, db, case):
    path = os.getcwd() + f'/tests/api/{case}/bundle.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    assert len(db.session.query(PendingBundle).all()) == 0

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_build_catalog(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    artists = db.session.query(Artist).all()
    assert len(artists) == 7
    catalogs = db.session.query(Catalog).all()
    assert len(catalogs) == 2
    tracks = db.session.query(Track).all()
    assert len(tracks) == 23
    bundles = db.session.query(Bundle).all()
    assert len(bundles) == 2
    bundles = db.session.query(BundleVersionTable).all()
    assert len(bundles) == 4
    # assert bundles[0].bundle_id == 2
    # assert bundles[0].version_id == 1 

    # assert bundles[1].bundle_id == 2
    # assert bundles[1].version_id == 3

    # assert bundles[2].bundle_id == 1
    # assert bundles[2].version_id == 5

    # assert bundles[3].bundle_id == 1
    # assert bundles[3].version_id == 3

def test_can_import_bandcamp(test_client, db):
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    assert len(result) == 34
    sum = db.session.query(func.sum(IncomePending.amount)).one()[0]
    assert sum == Decimal('284.59')
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '5555555'
    assert json.loads(response.data)['data']['attributes']['length'] == 34

def test_can_process_pending_income(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 37   

    bundles = db.session.query(IncomeTotal).filter(IncomeTotal.version_id == None).all()
    assert len(bundles) == 0

    sum = db.session.query(func.sum(IncomeTotal.amount)).one()[0]
    assert sum == Decimal('284.59')

def test_statement_with_no_previous_balance(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE) 
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31',
            }
    start_date = data['start_date']
    end_date = data['end_date']
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    response = test_client.post('/statements/1/generate-summary', data=json_data)


    metadata = MetaData(db.engine)
    metadata.reflect()
    statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')

    sum = db.session.query(func.sum(statement_table.c.artist_net)).one()[0]
    assert sum == Decimal('284.59')


    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 142.29,
                'previous_balance': 'statement_balance_none',
                'previous_balance_id': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [
                    {
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 91.08,
                    'split': 91.08,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 182.16,
                    'total_to_split': 182.16,
                    },
                    {
                    'id': 2,
                    'artist_name': 'Various Artists',
                    'balance_forward': 0.0,
                    'split': 0.0,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 0.0,
                    'total_to_split': 0.0
                    },
                    {
                    'id': 3,
                    'artist_name': 'Jimi Jeans',
                    'balance_forward': 11.38,
                    'split': 11.38,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.76,
                    'total_to_split': 22.76,
                    },
                    {
                    'id': 4,
                    'artist_name': 'Pop Rocks',
                    'balance_forward': 17.07,
                    'split': 17.07,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 34.14,
                    'total_to_split': 34.14
                    },
                    {
                    'id': 5,
                    'artist_name': 'Poor Boy',
                    'balance_forward': 11.38,
                    'split': 11.38,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.76,
                    'total_to_split': 22.76,
                    },
                    {
                    'id': 6,
                    'artist_name': 'Pineapple Party',
                    'balance_forward': 5.69,
                    'split': 5.69,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.38,
                    'total_to_split': 11.38,
                    },
                    {
                    'id': 7,
                    'artist_name': 'Chimichanga',
                    'balance_forward': 5.69,
                    'split': 5.69,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.38,
                    'total_to_split': 11.38,
                    },
                    ]
            }

