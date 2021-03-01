import os
import pytest

import datetime
import json

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal

base = os.path.basename(__file__)
case = base.split('.')[0]

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


def add_order_fees(test_client, db, case):
    data = [
            {
                'distributor_id': 1,
                'order_percentage': 0,
                'order_fee': 3.00, 
                'order_limit': 5.00
            },
            ]
    json_data = json.dumps(data)
    response = test_client.put('/settings/order-fee', data=json_data)

def test_statement(test_client, db):
    import_catalog(test_client, db, case)
    add_order_fees(test_client, db, case)
    import_bandcamp_sales(test_client, db, case)
    result = db.session.query(IncomePending).all()

    response = test_client.get('/income/refund-matching-errors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 2
    id1 = json.loads(response.data)[0]['id']
    id2 = json.loads(response.data)[1]['id']

    data = {
            'error_type': 'refund',
            'selected_ids': [id1],
            'new_value' : '-8.57'
            }
    json_data=json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert response.status_code == 200

    data = {
            'error_type': 'refund',
            'selected_ids': [id2],
            'new_value' : '0'
            }
    json_data=json.dumps(data)
    response = test_client.put('/income/update-errors', data=json_data)
    assert response.status_code == 200

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
                'statement_total': 131.15,
                'previous_balance': 'statement_balance_none',
                'previous_balance_id': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [{
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 131.15,
                    'split': 131.15,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 262.3,
                    'total_to_split': 262.3
                    }],
            }

