import os
import pytest

import datetime
import json

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal

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
    artists = db.session.query(Artist).all()
    assert len(artists) == 7
    catalogs = db.session.query(Catalog).all()
    assert len(catalogs) == 1
    tracks = db.session.query(Track).all()
    assert len(tracks) == 10

def test_can_import_bandcamp(test_client, db):
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    assert len(result) == 31
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '5555555'
    assert json.loads(response.data) == {
            'success': 'true',
            'data': {'attributes': {'length': 31, 'title': 'bandcamp.csv'},
                       'id': 'bandcamp.csv',
                       'type': 'db'}}


def test_can_process_pending_income(test_client, db):
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 31

def test_statement_with_no_previous_balance(test_client, db):
    import_catalog(test_client, db, CASE)
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
    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 134.6,
                'previous_balance': 'statement_balance_none',
                'previous_balance_id': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [
                    {
                    'id': 1,
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
                    'id': 2,
                    'artist_name': 'Jimi Jeans',
                    'balance_forward': 26.92,
                    'split': 26.92,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 53.83,
                    'total_to_split': 53.83,
                    },
                    {
                    'id': 3,
                    'artist_name': 'Pop Rocks',
                    'balance_forward': 40.38,
                    'split': 40.38,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 80.75,
                    'total_to_split': 80.75,
                    },
                    {
                    'id': 4,
                    'artist_name': 'Poor Boy',
                    'balance_forward': 26.92,
                    'split': 26.92,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 53.83,
                    'total_to_split': 53.83
                    },
                    {
                    'id': 5,
                    'artist_name': 'Stevie G',
                    'balance_forward': 13.46,
                    'split': 13.46,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 26.92,
                    'total_to_split': 26.92,
                    },
                    {
                    'id': 6,
                    'artist_name': 'Pineapple Party',
                    'balance_forward': 13.46,
                    'split': 13.46,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 26.92,
                    'total_to_split': 26.92,
                    },
                    {
                    'id': 7,
                    'artist_name': 'Chimichanga',
                    'balance_forward': 13.46,
                    'split': 13.46,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 26.92,
                    'total_to_split': 26.92,
                    },
                    ]
            }

