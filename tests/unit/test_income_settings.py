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
    assert len(json.loads(response.data)) == 0

def test_can_add_order_fee(test_client, db):
    data = {'distributor_id': 1,
            'order_percentage': 0.03,
            'order_fee': 2.00
            }
    json_data = json.dumps(data)
    response = test_client.post('/settings/order-fee', data=json_data)
    assert response.status_code == 200
    assert len(db.session.query(OrderSettings).all()) > 0
    """Check value."""
    response = test_client.get('/settings/order-fee')
    assert response.status_code == 200
    assert json.loads(response.data)
    assert json.loads(response.data)[0]['distributor_id'] == 1
    assert json.loads(response.data)[0]['order_percentage'] == 0.03
    assert json.loads(response.data)[0]['order_fee'] == 2.00


