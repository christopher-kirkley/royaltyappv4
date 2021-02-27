import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

def import_catalog(test_client, db, case):
    path = os.getcwd() + f'/tests/api/{case}/catalog.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-catalog',
            data=data)
    path = os.getcwd() + f"/tests/api/{case}/version.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-version',
            data=data)
    path = os.getcwd() + f"/tests/api/{case}/track.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/catalog/import-track',
            data=data)
    path = os.getcwd() + f"/tests/api/{case}/bundle.csv"
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    response = test_client.post('/income/process-pending')
    return response
