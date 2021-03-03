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

def test_statement_summary_with_master_and_physical(test_client, db):
    import_catalog(test_client, db, CASE)
    import_sales(test_client, db, CASE)
    response = test_client.post('/income/process-pending')
    path = os.getcwd() + f"/tests/api/{CASE}/sdphysical.csv"
    data = {
            'statement_source': 'sdphysical'
            }
    data['file'] = (path, 'sdphysical.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")

    response = test_client.post('/income/process-pending')

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

    """ Check detail query """
    metadata = MetaData(db.engine)
    metadata.reflect()
    statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')
    artist_id = 1

    assert len(db.session.query(statement_table).all()) == 4

    join_on_track = (
        db.session.query(
            cast((statement_table.c.artist_net), Numeric(8, 2)).label('net'),
            statement_table.c.quantity.label('quantity'),
            statement_table.c.transaction_type.label('transaction_type'),
            statement_table.c.medium.label('medium'),
            TrackCatalogTable.c.catalog_id.label('catalog_id')
            )
            .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
            .filter(statement_table.c.artist_id == artist_id)
        )

    assert len(join_on_track.all()) == 1

    join_on_version = (
        db.session.query(
            cast((statement_table.c.artist_net), Numeric(8, 2)).label('net'),
            statement_table.c.quantity.label('quantity'),
            statement_table.c.transaction_type.label('transaction_type'),
            statement_table.c.medium.label('medium'),
            Version.catalog_id.label('catalog_id')
            )
            .join(Version, statement_table.c.version_id == Version.id)
            .filter(statement_table.c.artist_id == artist_id)
        )

    assert len(join_on_version.all()) == 3

    joined_table = join_on_track.union_all(join_on_version).subquery()

    assert len(db.session.query(joined_table).all()) == 4

    statement_detail = (
            db.session.query(
                cast(func.sum(joined_table.c.net), Numeric(8, 2)).label('net'),
                Catalog.catalog_name.label('catalog_name'),
                func.sum(joined_table.c.quantity.label('quantity')),
                joined_table.c.transaction_type.label('transaction_type'),
                joined_table.c.medium.label('medium'),
            )
            .join(Catalog, joined_table.c.catalog_id == Catalog.id)
            .group_by(
                Catalog.catalog_name,
                joined_table.c.transaction_type,
                joined_table.c.medium,
                )
        )

    assert len(statement_detail.all()) == 2

    combined_sales = statement_detail.filter(joined_table.c.transaction_type == 'income').subquery()


    """ Check statement """
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        'advance': [],
          'album_sales': [{'catalog_name': 'Amazing',
                           'format': 'lp',
                           'net': 30.0,
                           'quantity': 3,
                           'version_number': 'TEST-01lp'}],
          'artist': 'Bonehead',
          'expense': [],
          'income': [
                     {'catalog_name': 'Amazing',
                      'combined_net': 1530.0,
                      'digital_net': 0,
                      'master_net': 1500.0,
                      'physical_net': 30.0}],
          'master_sales': [{'net': 1500.0,
                            'notes': 'Sync for film No More Chicken',
                            'track_name': 'Poetry'}],
          'statement': 'statement_2020_01_01_2020_01_31',
          'summary': [{'advances': 0.0,
                       'balance_forward': 765.0,
                       'previous_balance': 0.0,
                       'recoupables': 0.0,
                       'sales': 1530.0,
                       'split': 765.0,
                       'total_to_split': 1530.0}],
          'track_sales': []}


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
    statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')

    res =  db.session.query(statement_table)
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

    # income_summary = va.get_income_summary(table, 1)
    # assert income_summary == ''
    
    artist_id = 1

    statement_detail = (
        db.session.query(
            cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net'),
            Catalog.catalog_name.label('catalog_name'),
            func.sum(statement_table.c.quantity.label('quantity')),
            )
            .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
            .join(Catalog, TrackCatalogTable.c.catalog_id == Catalog.id)
            .group_by(Catalog.catalog_name)
            .filter(statement_table.c.artist_id == artist_id)
        )

    assert len(statement_detail.all()) > 0



    
    response = test_client.get('/statements/1/artist/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
        'advance': [],
          'album_sales': [],
          'artist': 'Bonehead',
          'expense': [],
          'income': [{'catalog_name': 'Amazing',
                      'combined_net': 1500.0,
                      'digital_net': 0,
                      'master_net': 1500.0,
                      'physical_net': 0.0}],
          'master_sales': [{'net': 1500.0,
                            'notes': 'Sync for film No More Chicken',
                            'track_name': 'Poetry'}],
          'statement': 'statement_2020_01_01_2020_01_31',
          'summary': [{'advances': 0.0,
                       'balance_forward': 750.0,
                       'previous_balance': 0.0,
                       'recoupables': 0.0,
                       'sales': 1500.0,
                       'split': 750.0,
                       'total_to_split': 1500.0}],
          'track_sales': []}
