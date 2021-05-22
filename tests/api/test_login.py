import os
import pytest

import datetime
import json
import time

from royaltyapp.models import Artist, Catalog, Version, Track, IncomePending, IncomeTotal, Bundle, User, db, add_admin_user

from royaltyapp.income.helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors, find_distinct_refund_matching_errors

from werkzeug.security import generate_password_hash, check_password_hash

from flask import request

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def test_can_login_admin(test_client, db):
    add_admin_user(db)
    res = db.session.query(User).all()
    assert len(res) != 0
    assert res[0].email == 'admin@admin.com'
    hashed_password = res[0].password 
    assert check_password_hash(hashed_password, 'password')

    data = {'email': 'admin@admin.com',
            'password': 'password',
            }
    json_data = json.dumps(data)
    response = test_client.post('/login', data=json_data)
    assert response.status_code == 200
    res = db.session.query(User).first()
    assert res.email == 'admin@admin.com'
    hashed_password = res.password
    assert check_password_hash(hashed_password, 'password')

def test_can_add_user(test_client, db):
    data = {'email': 'bob@bob.com',
            'password': 'password',
            }
    json_data = json.dumps(data)
    response = test_client.post('/register', data=json_data)
    assert response.status_code == 200
    res = db.session.query(User).first()
    assert res.email == 'bob@bob.com'
    hashed_password = res.password
    assert check_password_hash(hashed_password, 'password')

def test_can_generate_user_cookies(test_client, db):
    add_admin_user(db)
    data = {'email': 'admin@admin.com',
            'password': 'password',
            }
    json_data = json.dumps(data)
    response = test_client.post('/login', data=json_data)
    assert response.status_code == 200
    assert response.headers['Set-Cookie']
    
def test_can_logout(test_client, db):
    add_admin_user(db)
    res = db.session.query(User).all()
    assert len(res) != 0
    assert res[0].email == 'admin@admin.com'
    hashed_password = res[0].password 
    assert check_password_hash(hashed_password, 'password')

    data = {'email': 'admin@admin.com',
            'password': 'password',
            }
    json_data = json.dumps(data)
    response = test_client.post('/login', data=json_data)
    assert response.status_code == 200
    response = test_client.post('/logout')
    assert response.status_code == 200
    assert response.headers['Set-Cookie']

# Flask request needed for JWT decorator
