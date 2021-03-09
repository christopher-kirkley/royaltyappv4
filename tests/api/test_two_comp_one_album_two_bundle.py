import os
import pytest

import datetime
import json

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle, BundleVersionTable, PendingBundle

from sqlalchemy import func, MetaData

from decimal import Decimal


from royaltyapp.statements.util import generate_statement as ge
from royaltyapp.statements.util import generate_artist_statement as ga
from royaltyapp.statements.util import view_artist_statement as va

import time

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

def import_bundle(test_client, db, case):
    path = os.getcwd() + f'/tests/api/{case}/bundle.csv'
    f = open(path, 'rb')
    data = {
            'CSV': f
            }
    response = test_client.post('/bundle/import-bundle',
            data=data)
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    assert len(db.session.query(PendingBundle).all()) == 0

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_can_build_catalog(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    artists = db.session.query(Artist).all()
    assert len(artists) == 7
    catalogs = db.session.query(Catalog).all()
    assert len(catalogs) == 2
    tracks = db.session.query(Track).all()
    assert len(tracks) == 23
    bundles = db.session.query(Bundle).all()
    assert len(bundles) == 2
    bundles = db.session.query(BundleVersionTable).all()
    assert len(bundles) == 4
    # assert bundles[0].bundle_id == 2
    # assert bundles[0].version_id == 1 

    # assert bundles[1].bundle_id == 2
    # assert bundles[1].version_id == 3

    # assert bundles[2].bundle_id == 1
    # assert bundles[2].version_id == 5

    # assert bundles[3].bundle_id == 1
    # assert bundles[3].version_id == 3

def test_can_import_bandcamp(test_client, db):
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    assert len(result) == 34
    sum = db.session.query(func.sum(IncomePending.amount)).one()[0]
    assert sum == Decimal('284.59')
    first = db.session.query(IncomePending).first()
    assert first.date == datetime.date(2020, 1, 1)
    assert first.upc_id == '5555555'
    assert json.loads(response.data)['data']['attributes']['length'] == 34

def test_can_process_pending_income(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE)
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')
    assert response.status_code == 200
    assert json.loads(response.data) == {'success': 'true'}
    res = db.session.query(IncomeTotal).all()
    assert len(res) == 34

    bundles = db.session.query(IncomeTotal).filter(IncomeTotal.bundle_id != None).all()
    assert len(bundles) == 3

    assert bundles[0].bundle_id == 2
    assert bundles[1].bundle_id == 2
    assert bundles[2].bundle_id == 1

    sum = db.session.query(func.sum(IncomeTotal.amount)).one()[0]
    assert sum == Decimal('284.59')

def test_make_subquery_to_generate_statement(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE) 
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')

    """ Unit tests."""
    start_date = '2020-01-01'
    end_date = '2020-01-31'
    previous_balance_id = 0
    date_range = (str(start_date) + '_' + str(end_date)).replace('-', '_')
    table = ge.create_statement_table(date_range)
    table_obj = table.__table__
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_index = ge.add_statement_to_index(table, statement_summary_table)

    statement_balance_table = ge.create_statement_balance_table(table.__table__)
    ge.add_statement_balance_to_index(statement_index.id, statement_balance_table)

    if previous_balance_id == 'opening_balance':
        ge.add_opening_balance_to_index(id)
    else:
        ge.add_previous_balance_id_to_index(statement_index.id, previous_balance_id)

    assert len(db.session.query(IncomeTotal).all()) == 34


    # artist_catalog_percentage = ge.find_track_percentage()
    # artist_total = ge.find_artist_total(start_date, end_date, artist_catalog_percentage)

    """ Make IncomeTotal subquery with split bundles into versions """
    count_per_bundle = (db.session.query(BundleVersionTable.c.bundle_id,
                                     func.count(BundleVersionTable.c.bundle_id)
                                     .label('version_count'))
                    .group_by(BundleVersionTable.c.bundle_id)
                    .subquery()
                    )

    sel = (db.session
            .query(
                (IncomeTotal.transaction_type).label('transaction_type'),
                IncomeTotal.date.label('date'),
                IncomeTotal.quantity.label('quantity'),
                (IncomeTotal.label_net / count_per_bundle.c.version_count).label('label_net'),
                IncomeTotal.type.label('type'),
                IncomeTotal.medium.label('medium'),
                IncomeTotal.income_distributor_id.label('distributor_id'),
                (BundleVersionTable.c.version_id).label('version_id'),
                IncomeTotal.track_id.label('track_id'),
                IncomeTotal.customer.label('customer'),
                IncomeTotal.notes.label('notes'),
                IncomeTotal.city.label('city'),
                IncomeTotal.region.label('region'),
                IncomeTotal.country.label('country'),
                )
            .join(count_per_bundle, count_per_bundle.c.bundle_id == IncomeTotal.bundle_id)
            .join(BundleVersionTable, BundleVersionTable.c.bundle_id == IncomeTotal.bundle_id)
         )

    assert len(sel.all()) == 6
    assert sel.all()[0].label_net == Decimal('2.57')
    assert sel.all()[0].version_id == 1
    assert sel.all()[1].label_net == Decimal('2.57')
    assert sel.all()[1].version_id == 1
    assert sel.all()[2].label_net == Decimal('2.57')
    assert sel.all()[2].version_id == 3
    assert sel.all()[3].label_net == Decimal('2.57')
    assert sel.all()[3].version_id == 3
    assert sel.all()[4].label_net == Decimal('2.57')
    assert sel.all()[4].version_id == 5
    assert sel.all()[5].label_net == Decimal('2.57')
    assert sel.all()[5].version_id == 3

    """Query for albums, calculate artist total per catalog item."""
    albums = (db.session.query(
            IncomeTotal.transaction_type.label('transaction_type'),
            IncomeTotal.date,
            IncomeTotal.quantity,
            IncomeTotal.label_net,
            IncomeTotal.type,
            IncomeTotal.medium,
            IncomeTotal.income_distributor_id,
            IncomeTotal.version_id,
            IncomeTotal.track_id,
            IncomeTotal.customer,
            IncomeTotal.notes,
            IncomeTotal.city,
            IncomeTotal.region,
            IncomeTotal.country
            )
            .filter(IncomeTotal.bundle_id == None))

    joined = sel.union_all(albums).subquery()

    assert len(db.session.query(joined).all()) == 37

    assert db.session.query(func.sum(joined.c.label_net)).first()[0] == Decimal('284.59')
    assert db.session.query(joined.c.transaction_type).first()[0] == 'income'

def test_subquery_function(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE) 
    result = db.session.query(IncomePending).all()
    response = test_client.post('/income/process-pending')

    subquery = ge.split_bundles_to_versions()

    assert len(db.session.query(subquery).all()) == 37

    assert len(db.session.query(subquery.c.label_net).all()) == 37
    assert len(db.session.query(subquery.c.date).all()) == 37

def test_statement_with_no_previous_balance(test_client, db):
    import_catalog(test_client, db, CASE)
    import_bundle(test_client, db, CASE)
    response = import_bandcamp_sales(test_client, db, CASE) 
    result = db.session.query(IncomePending).all()
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


    metadata = MetaData(db.engine)
    metadata.reflect()
    statement_table = metadata.tables.get('statement_2020_01_01_2020_01_31')

    sum = db.session.query(func.sum(statement_table.c.artist_net)).one()[0]
    assert sum == Decimal('284.59')


    response = test_client.get('/statements/1')
    assert response.status_code == 200
    assert json.loads(response.data) == {
            'summary': {
                'statement_total': 142.29,
                'previous_balance': 'statement_balance_none',
                'previous_balance_id': 0,
                'statement': 'statement_2020_01_01_2020_01_31',
                },
            'detail':
                [
                    {
                    'id': 1,
                    'artist_name': 'Bonehead',
                    'balance_forward': 91.08,
                    'split': 91.08,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 182.16,
                    'total_to_split': 182.16,
                    },
                    {
                    'id': 2,
                    'artist_name': 'Various Artists',
                    'balance_forward': 0.0,
                    'split': 0.0,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 0.0,
                    'total_to_split': 0.0
                    },
                    {
                    'id': 3,
                    'artist_name': 'Jimi Jeans',
                    'balance_forward': 11.38,
                    'split': 11.38,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.76,
                    'total_to_split': 22.76,
                    },
                    {
                    'id': 4,
                    'artist_name': 'Pop Rocks',
                    'balance_forward': 17.07,
                    'split': 17.07,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 34.14,
                    'total_to_split': 34.14
                    },
                    {
                    'id': 5,
                    'artist_name': 'Poor Boy',
                    'balance_forward': 11.38,
                    'split': 11.38,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 22.76,
                    'total_to_split': 22.76,
                    },
                    {
                    'id': 6,
                    'artist_name': 'Pineapple Party',
                    'balance_forward': 5.69,
                    'split': 5.69,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.38,
                    'total_to_split': 11.38,
                    },
                    {
                    'id': 7,
                    'artist_name': 'Chimichanga',
                    'balance_forward': 5.69,
                    'split': 5.69,
                    'total_advance': 0.0,
                    'total_previous_balance': 0.0,
                    'total_recoupable': 0.0,
                    'total_sales': 11.38,
                    'total_to_split': 11.38,
                    },
                    ]
            }

