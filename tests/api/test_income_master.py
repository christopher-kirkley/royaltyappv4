import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

from sqlalchemy import MetaData
from decimal import Decimal

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
    path = os.getcwd() + f"/tests/api/{case}/bundle.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200

def import_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/master.csv"
    data = {
            'statement_source': 'master'
            }
    data['file'] = (path, 'master.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_import_master(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).all()
    assert (db.session.query(IncomePending).first().notes) == 'Sync for film No More Chicken'
    assert len(query) == 1

def test_can_process_pending(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 1
    track_id = db.session.query(Track).filter(Track.isrc=='ABC000000004').first().id
    res = db.session.query(IncomeTotal).filter(IncomeTotal.track_id==track_id)
    assert len(res.all()) == 1
    assert res.first().medium == 'master'
    assert res.first().type == 'track'
    assert res.first().amount == Decimal('1500')
    assert res.first().label_net == Decimal('1500')
    assert res.first().notes == 'Sync for film No More Chicken'

def test_can_make_statement_summary(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    response = test_client.post('/statements/1/generate-summary')
    assert response.status_code == 200


    """ Check table created """
    metadata = MetaData(db.engine)
    metadata.reflect()
    table = metadata.tables.get('statement_2020_01_01_2020_01_31')

    res =  db.session.query(table)
    assert len(res.all()) == 1
    assert res.first().notes == 'Sync for film No More Chicken'

    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 750.0,
                'previous_balance_id': 0,
                'previous_balance': 'statement_balance_none',
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'artist_name': 'Bonehead',
                    'balance_forward': 750.0,
                    'id': 1,
                    'split': 750.0,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 1500.0,
                    'total_to_split': 1500.0}

                    ]
                }

    
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {}
