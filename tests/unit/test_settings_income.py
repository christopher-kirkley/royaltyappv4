import pytest
import json
import datetime
import time

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense, add_bandcamp_errors

def test_can_get_distributors(test_client, db):
    response = test_client.get('/income/distributors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0
    assert json.loads(response.data)[0]['distributor_name'] == 'bandcamp'

def test_can_get_order_fees(test_client, db):
    response = test_client.get('/settings/order-fee')
    assert response.status_code == 200
    assert json.loads(response.data)[0] == {
            'distributor_name': 'bandcamp',
            'order_fee': 0.0,
            'order_percentage': 0.0,
            'order_limit': 0.0,
            }
    # assert len(json.loads(response.data)) == 5
# def test_can_add_order_fee(test_client, db):
#     data = {'distributor_id': 1,
#             'order_percentage': 0.03,
#             'order_fee': 2.00
#             }
#     json_data = json.dumps(data)
#     response = test_client.post('/settings/order-fee', data=json_data)
#     assert response.status_code == 200
#     assert len(db.session.query(OrderSettings).all()) > 0
#     """Check value."""
#     response = test_client.get('/settings/order-fee')
#     assert response.status_code == 200
#     assert json.loads(response.data)
#     assert json.loads(response.data)[0]['distributor_id'] == 1
#     assert json.loads(response.data)[0]['order_percentage'] == 0.03
#     assert json.loads(response.data)[0]['order_fee'] == 2.00

def test_can_update_order_fee(test_client, db):
    data = [
            {
                'distributor_id': 1,
                'order_percentage': 0.04,
                'order_fee': 3.00, 
                'order_limit': 5.00
            },
            {
                'distributor_id': 2,
                'order_percentage': 0.04,
                'order_fee': 3.00,
                'order_limit': 5.00
            },
            ]
    json_data = json.dumps(data)
    response = test_client.put('/settings/order-fee', data=json_data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    assert len(db.session.query(OrderSettings).all()) > 0
    assert db.session.query(OrderSettings).filter(OrderSettings.distributor_id == 1).first().distributor_id == 1
    assert db.session.query(OrderSettings).filter(OrderSettings.distributor_id == 1).first().order_percentage == 0.04

    # response = test_client.get('/settings/order-fee')
    # assert response.status_code == 200
    # assert json.loads(response.data) == ''
    # assert json.loads(response.data)[0]['distributor_id'] == 1
    # assert json.loads(response.data)[0]['order_percentage'] == 0.04
    # assert json.loads(response.data)[0]['order_fee'] == 2.00
