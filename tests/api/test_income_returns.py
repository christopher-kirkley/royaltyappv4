import os
import pytest

import datetime
import json
import time
from decimal import Decimal

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle

from helpers import import_catalog

from sqlalchemy import func

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def import_bandcamp_sales(test_client, db, case):
    path = os.getcwd() + f"/tests/api/{case}/bandcamp.csv"
    data = {
            'statement_source': 'bandcamp'
            }
    data['file'] = (path, 'bandcamp.csv')
    response = test_client.post('/income/import-sales',
            data=data, content_type="multipart/form-data")
    return response

def test_reversal_errors(test_client, db):

    import_catalog(test_client, db, CASE)
    import_bandcamp_sales(test_client, db, CASE)
    sel = db.session.query(IncomePending).filter(IncomePending.description == 'REVERSAL').subquery()
    assert len(db.session.query(sel).all()) == 10
    assert db.session.query(func.sum(sel.c.amount)).first()[0] == Decimal('0')


# def test_can_import_refund(test_client, db):
#     import_catalog(test_client, db, CASE)
#     import_bandcamp_sales(test_client, db, CASE)
#     assert len(db.session.query(IncomePending).all()) == 4
#     res = db.session.query(IncomePending).filter(IncomePending.order_id == '123').one()
#     assert res.medium == 'physical'
#     assert res.type == 'album'
#     assert res.album_name == 'Amazing'
#     assert res.upc_id == '1111111111'
#     assert res.amount == Decimal('10.150000000000000000')
#     res = db.session.query(IncomePending).filter(IncomePending.order_id == 't281131841').one()
#     assert res.medium == 'physical'
#     assert res.upc_id == '1111111111'
#     assert res.amount == Decimal('-6.670000000000000000')

#     res = db.session.query(IncomePending).filter(IncomePending.order_id == 't281134968').all()
#     assert len(res) == 2
#     assert res[0].amount == Decimal('-7.7200000000000000000')
#     assert res[0].order_id == 't281134968'
#     assert res[1].amount == None
#     assert res[1].order_id == 't281134968'

#     """ Check refund errors. """
#     response = test_client.get('/income/refund-matching-errors')
#     assert response.status_code == 200
#     assert len(json.loads(response.data)) == 2


# def test_can_update_refund_errors(test_client, db):
#     import_catalog(test_client, db, CASE)
#     import_bandcamp_sales(test_client, db, CASE)

#     res = db.session.query(IncomePending).filter(IncomePending.id == 4).one()
#     assert res.amount == None

#     data = {
#             'error_type': 'refund',
#             'selected_ids': [4],
#             'new_value' : '-3'
#             }
#     json_data=json.dumps(data)
#     response = test_client.put('/income/update-errors', data=json_data)
#     assert response.status_code == 200

#     res = db.session.query(IncomePending).filter(IncomePending.id == 4).one()
#     assert res.amount == Decimal('-3.000000000000000000')
