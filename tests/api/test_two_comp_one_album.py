import os
import pytest

import datetime
import json

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal

CASE='two_comp_one_album'

def import_catalog(test_client, db, case):
    path = os.getcwd() + f'/tests/test_cases/{case}/catalog.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/test_cases/{case}/version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    assert response.status_code == 200
    path = os.getcwd() + f"/tests/test_cases/{case}/track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    assert response.status_code == 200

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/test_cases/{case}/bandcamp.csv"
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
    assert len(catalogs) == 2
    tracks = db.session.query(Track).all()
    assert len(tracks) == 23

def test_can_import_bandcamp(test_client, db):
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    assert len(result) == 31
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '5555555'
    assert json.loads(response.data) == {'success': 'true'}

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
                'previous_balance': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [
                    {
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 84.53,
                    'split': 84.53,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 169.05,
                    'total_to_split': 169.05,
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
                    'balance_forward': 11.13,
                    'split': 11.13,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.25,
                    'total_to_split': 22.25,
                    },
                    {
                    'id': 4,
                    'artist_name': 'Pop Rocks',
                    'balance_forward': 16.69,
                    'split': 16.69,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 33.37,
                    'total_to_split': 33.37
                    },
                    {
                    'id': 5,
                    'artist_name': 'Poor Boy',
                    'balance_forward': 11.13,
                    'split': 11.13,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.25,
                    'total_to_split': 22.25,
                    },
                    {
                    'id': 6,
                    'artist_name': 'Pineapple Party',
                    'balance_forward': 5.56,
                    'split': 5.56,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.12,
                    'total_to_split': 11.12,
                    },
                    {
                    'id': 7,
                    'artist_name': 'Chimichanga',
                    'balance_forward': 5.56,
                    'split': 5.56,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.12,
                    'total_to_split': 11.12,
                    },
                    ]
            }

