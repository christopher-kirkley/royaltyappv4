import pytest
import json
import datetime
import time
from decimal import Decimal

import os
import io

import pandas as pd
import numpy as np

from sqlalchemy import func

from royaltyapp.models import Artist, Catalog, Version, Track, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_bandcamp_order_settings, add_artist_expense, add_bandcamp_errors

def test_can_get_distributors(test_client, db):
    response = test_client.get('/income/distributors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0
    assert json.loads(response.data)[0]['distributor_name'] == 'bandcamp'

def test_can_get_order_fees(test_client, db):
    response = test_client.get('/settings/order-fee')
    assert response.status_code == 200
    assert json.loads(response.data)[0] == {
            'distributor_id': 1,
            'distributor_name': 'bandcamp',
            'order_fee': 0.0,
            'order_percentage': 0.0,
            'order_limit': 0.0,
            }

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
    assert db.session.query(OrderSettings).filter(OrderSettings.distributor_id == 1).first().order_fee == 3.00
    assert db.session.query(OrderSettings).filter(OrderSettings.distributor_id == 1).first().order_limit == 5.00

def test_order_fee_changes_income(test_client, db):
    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 7
    row1 = db.session.query(IncomeTotal).filter(IncomeTotal.id == 1).one()
    assert row1.amount == Decimal('10.15')
    assert row1.label_net == Decimal('10.15')
    assert row1.label_fee == Decimal('0')

    """Delete income table, and reprocess."""
    income_total = IncomeTotal.query.delete()
    db.session.commit()
    assert len(db.session.query(IncomeTotal).all()) == 0

    """Change order fees."""
    data = [
            {
                'distributor_id': 1,
                'order_percentage': 0,
                'order_fee': 3, 
                'order_limit': 0
            }
            ]
    json_data = json.dumps(data)
    response = test_client.put('/settings/order-fee', data=json_data)
    assert response.status_code == 200

    add_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert len(db.session.query(IncomeTotal).all()) == 7
    row1 = db.session.query(IncomeTotal).filter(IncomeTotal.id == 8).one()
    assert row1.amount == Decimal('10.15')
    assert row1.label_fee == Decimal('3')
    assert row1.label_net == Decimal('7.15')

def test_order_percentage_changes_income(test_client, db):
    """Change order fees."""
    data = [
            {
                'distributor_id': 1,
                'order_percentage': 0.05,
                'order_fee': 0, 
                'order_limit': 0
            }
            ]
    json_data = json.dumps(data)
    response = test_client.put('/settings/order-fee', data=json_data)
    assert response.status_code == 200

    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    row1 = db.session.query(IncomeTotal).filter(IncomeTotal.id == 1).one()
    assert row1.amount == Decimal('10.15')
    assert row1.label_fee == Decimal('0.51')
    assert row1.label_net == Decimal('9.64')

def test_only_apply_fee_on_limit(test_client, db):
    """Change order fees."""
    data = [
            {
                'distributor_id': 1,
                'order_percentage': 0,
                'order_fee': 3, 
                'order_limit': 7
            }
            ]
    json_data = json.dumps(data)
    response = test_client.put('/settings/order-fee', data=json_data)
    assert response.status_code == 200

    build_catalog(db, test_client)
    add_bandcamp_sales(test_client)
    response = test_client.post('/income/process-pending')
    row1 = db.session.query(IncomeTotal).filter(IncomeTotal.id == 1).one()
    assert row1.amount == Decimal('10.15')
    assert row1.label_fee == Decimal('3')
    assert row1.label_net == Decimal('7.15')
    row2 = db.session.query(IncomeTotal).filter(IncomeTotal.id == 2).one()
    assert row2.amount == Decimal('6.26')
    assert row2.label_fee == Decimal('0')
    assert row2.label_net == Decimal('6.26')


