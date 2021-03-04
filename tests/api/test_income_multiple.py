import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle, TrackCatalogTable

from royaltyapp.statements.util import view_artist_statement as va

from sqlalchemy import MetaData, cast, func, exc, Numeric
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

    path = os.getcwd() + f"/tests/api/{case}/sddigital.csv"
    data = {
            'statement_source': 'sddigital'
            }
    data['file'] = (path, 'sddigital.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

    path = os.getcwd() + f"/tests/api/{case}/sdphysical.csv"
    data = {
            'statement_source': 'sdphysical'
            }
    data['file'] = (path, 'sdphysical.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

    return response

def test_can_import_all_streams(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    query = db.session.query(IncomePending).all()
    assert len(query) == 10
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    query = db.session.query(IncomeTotal).all()
    assert len(query) == 10

def test_statement_summary_with_master_and_physical(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)

    """ Process income """
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200

    """Generate Summary"""
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

    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'detail': [{
                'artist_name': 'Bonehead',
                'balance_forward': 522.5,
                'id': 1,
                'split': 522.5,
                'total_advance': 0.0,
                'total_previous_balance': 0.0,
                'total_recoupable': 0.0,
                'total_sales': 1045.0,
                'total_to_split': 1045.0}],
            'summary': {
                'previous_balance': 'statement_balance_none',
                'previous_balance_id': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                'statement_total': 522.5}}

    """ Check table created """
    metadata = MetaData(db.engine)
    metadata.reflect()
    statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')

    # assert va.get_income_summary(statement_table, 1) == ''

    """ Check statement """
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'advance': [],
            'album_sales': [{
                'catalog_name': 'Amazing',
                'format': 'lp',
                'net': 30.0,
                'quantity': 3,
                'version_number': 'TEST-01lp'},
                {
                'catalog_name': 'Sampler',
                'format': 'digital',
                'net': 10.0,
                'quantity': None,
                'version_number': 'TEST-02digi'}],
            'artist': 'Bonehead',
            'expense': [],
            'income': [
                {
                'catalog_name': 'Amazing',
                'combined_net': 1035.0,
                'digital_net': 5.0,
                'master_net': 1000.0,
                'physical_net': 30.0
                },
                {
                'catalog_name': 'Sampler',
                'combined_net': 10.0,
                'digital_net': 10.0,
                'master_net': 0,
                'physical_net': 0
                }
                ],
            'master_sales': [{
                'net': 1000.0,
                'notes': 'Sync for film No More Chicken',
                'track_name': 'Poetry'}],
            'statement': 'statement_2020_01_01_2020_01_31',
            'summary': [{
                'advances': 0.0,
                'balance_forward': 522.5,
                'previous_balance': 0.0,
                'recoupables': 0.0,
                'sales': 1045.0,
                'split': 522.5,
                'total_to_split': 1045.0}],
              'track_sales': [
                  {
                  'net': 1.0,
                  'quantity': 1,
                  'track_name': 'Chicken'},
                  {'net': 1.0,
                   'quantity': 2,
                   'track_name': 'Fruitcake'},
                  {'net': 1.0,
                   'quantity': 2,
                   'track_name': 'New York Dreamin’'},
                  {'net': 1.0,
                   'quantity': 1,
                   'track_name': 'Pineapples'},
                  {'net': 1.0,
                   'quantity': 1,
                   'track_name': 'Poetry'}],
                  }


# def test_can_make_statement_summary(test_client, db):
#     import_catalog(test_client, db, CASE)
#     import_sales(test_client, db, CASE)
#     response = test_client.post('/income/process-pending')
#     assert response.status_code == 200
#     data = {
#             'previous_balance_id': 0,
#             'start_date': '2020-01-01',
#             'end_date': '2020-01-31'
#             }
#     json_data = json.dumps(data)
#     response = test_client.post('/statements/generate', data=json_data)
#     assert response.status_code == 200
#     response = test_client.post('/statements/1/generate-summary')
#     assert response.status_code == 200


#     """ Check table created """
#     metadata = MetaData(db.engine)
#     metadata.reflect()
#     statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')

#     res =  db.session.query(statement_table)
#     assert len(res.all()) == 1
#     assert res.first().notes == 'Sync for film No More Chicken'

#     response = test_client.get('/statements/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {
#             'summary': {
#                 'statement_total': 750.0,
#                 'previous_balance_id': 0,
#                 'previous_balance': 'statement_balance_none',
#                 'statement': 'statement_2020_01_01_2020_01_31',
#                 },
#             'detail':
#                 [{
#                     'artist_name': 'Bonehead',
#                     'balance_forward': 750.0,
#                     'id': 1,
#                     'split': 750.0,
#                     'total_advance': 0.0,
#                     'total_previous_balance': 0.0,
#                     'total_recoupable': 0.0,
#                     'total_sales': 1500.0,
#                     'total_to_split': 1500.0}

#                     ]
#                 }

#     # income_summary = va.get_income_summary(table, 1)
#     # assert income_summary == ''
    
#     artist_id = 1

#     statement_detail = (
#         db.session.query(
#             cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net'),
#             Catalog.catalog_name.label('catalog_name'),
#             func.sum(statement_table.c.quantity.label('quantity')),
#             )
#             .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
#             .join(Catalog, TrackCatalogTable.c.catalog_id == Catalog.id)
#             .group_by(Catalog.catalog_name)
#             .filter(statement_table.c.artist_id == artist_id)
#         )

#     assert len(statement_detail.all()) > 0



    
#     response = test_client.get('/statements/1/artist/1')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {
#         'advance': [],
#           'album_sales': [],
#           'artist': 'Bonehead',
#           'expense': [],
#           'income': [{'catalog_name': 'Amazing',
#                       'combined_net': 1500.0,
#                       'digital_net': 0,
#                       'master_net': 1500.0,
#                       'physical_net': 0.0}],
#           'master_sales': [{'net': 1500.0,
#                             'notes': 'Sync for film No More Chicken',
#                             'track_name': 'Poetry'}],
#           'statement': 'statement_2020_01_01_2020_01_31',
#           'summary': [{'advances': 0.0,
#                        'balance_forward': 750.0,
#                        'previous_balance': 0.0,
#                        'recoupables': 0.0,
#                        'sales': 1500.0,
#                        'split': 750.0,
#                        'total_to_split': 1500.0}],
#           'track_sales': []}
