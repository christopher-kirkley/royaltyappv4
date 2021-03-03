import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from decimal import Decimal
from sqlalchemy import MetaData

import time

from royaltyapp.models import StatementGenerated, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending

from royaltyapp.statements.util import generate_artist_statement as ga

from helpers import import_catalog, import_bandcamp_sales

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def test_can_generate_statement(test_client, db):
    data = {
            'previous_balance_id': 0,
            'start_date': '2020-01-01',
            'end_date': '2020-01-31'
            }
    json_data = json.dumps(data)
    response = test_client.post('/statements/generate', data=json_data)
    assert response.status_code == 200
    query = db.session.query(StatementGenerated).all()
    assert len(query) == 1
    m = MetaData()
    m.reflect(db.engine)
    table_list = [table.name for table in m.tables.values()]
    assert 'statement_2020_01_01_2020_01_31' in table_list
    assert 'statement_2020_01_01_2020_01_31_balance' in table_list
    assert 'statement_summary_2020_01_01_2020_01_31' in table_list


