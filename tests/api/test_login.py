import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle, User

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, find_distinct_refund_matching_errors

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def test_can_login(test_client, db):
    user = User(
            email='bob@bob.com',
            password='password'
            )
    db.session.add(user)
    db.session.commit()

    data = {'email': 'bob@bob.com',
            'password': 'password',
            }
    json_data = json.dumps(data)
    response = test_client.post('/login', data=json_data)
    assert response.status_code == 200

    
