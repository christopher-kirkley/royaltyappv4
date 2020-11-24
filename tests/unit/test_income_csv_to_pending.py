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

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense, add_bandcamp_errors, add_two_bandcamp_sales

def post_data(test_client, filename, import_type):
    path = os.getcwd() + '/tests/files/' + filename
    data = {
            'statement_source': import_type
            }
    data['file'] = (path, filename)
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

bandcamp_cases = {
        'import_bandcamp.csv': ('import_bandcamp.csv', {'records': 732, 'sum': 4626.58}),
        'import_bandcamp_2.csv': ('import_bandcamp_2.csv', {'records': 15, 'sum': 111.24}),
        }

sddigital_cases = {
        'import_sddigital.csv': ('import_sddigital.csv', {'records': 13, 'sum': 7.53}),
        }

sdphysical_cases = {
        'import_sdphysical.csv': ('import_sdphysical.csv', {'records': 43, 'sum': 35.32}),
        }

shopify_cases = {
        'import_shopify.csv': ('import_shopify.csv', {'records': 4, 'sum': 57.00}),
        }

sds_cases = {
        'import_sds.csv': ('import_sds.csv', {'records': 10, 'sum': 0.05496187}),
        }

quickbooks_cases = {
        'import_quickbooks.csv': ('import_quickbooks.csv', {'records': 2, 'sum': 1229.00}),
        }

@pytest.mark.parametrize('filename, expected', list(bandcamp_cases.values()), ids=list(bandcamp_cases.keys()))
def test_can_import_bandcamp(test_client, db, filename, expected):
    import_type = 'bandcamp'

    response = post_data(test_client, filename, import_type)

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert float(total) == expected['sum']


@pytest.mark.parametrize('filename, expected', list(sddigital_cases.values()), ids=list(sddigital_cases.keys()))
def test_can_import_sddigital(test_client, db, filename, expected):
    import_type = 'sddigital'

    response = post_data(test_client, filename, import_type)

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert round(float(total), 2) == expected['sum']

@pytest.mark.parametrize('filename, expected', list(sdphysical_cases.values()), ids=list(sdphysical_cases.keys()))
def test_can_import_sdphysical(test_client, db, filename, expected):
    import_type = 'sdphysical'

    response = post_data(test_client, filename, import_type)

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert round(float(total), 2) == expected['sum']

@pytest.mark.parametrize('filename, expected', list(shopify_cases.values()), ids=list(shopify_cases.keys()))
def test_can_import_shopify(test_client, db, filename, expected):
    response = post_data(test_client, filename, 'shopify')

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert round(float(total), 2) == expected['sum']

@pytest.mark.parametrize('filename, expected', list(sds_cases.values()), ids=list(sds_cases.keys()))
def test_can_import_sds(test_client, db, filename, expected):
    response = post_data(test_client, filename, 'sds')

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert float(total) == expected['sum']

@pytest.mark.parametrize('filename, expected', list(quickbooks_cases.values()), ids=list(quickbooks_cases.keys()))
def test_can_import_quickbooks(test_client, db, filename, expected):
    response = post_data(test_client, filename, 'quickbooks')

    """ Check response. """
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['data']['attributes']['length'] == expected['records']

    """ Check db """
    assert len(db.session.query(IncomePending).all()) == expected['records']
    total = (db.session
            .query(func.sum(IncomePending.amount))
            .one()[0])
    assert round(float(total), 2) == expected['sum']

