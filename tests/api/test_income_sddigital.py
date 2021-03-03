import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

from sqlalchemy import MetaData

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
    path = os.getcwd() + f"/tests/api/{case}/sddigital.csv"
    data = {
            'statement_source': 'sddigital'
            }
    data['file'] = (path, 'sddigital.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_import_digital(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    assert len(db.session.query(IncomePending).all()) == 5  

def test_can_process_pending(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 5


def test_can_generate_statement(test_client, db):
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
    assert len(res.all()) == 5
    assert res.first().catalog_id == None

    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 0.04,
                'previous_balance_id': 0,
                'previous_balance': 'statement_balance_none',
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'artist_name': 'Bonehead',
                    'balance_forward': 0.04,
                    'id': 1,
                    'split': 0.04,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 0.08,
                    'total_to_split': 0.08}

                    ]
                }

    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {}

