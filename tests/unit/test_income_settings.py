import pytest
import json
import datetime
import time

import os
import io

import pandas as pd
import numpy as np

from royaltyapp.models import Artist, Catalog, Version, Track, Pending, PendingVersion, IncomePending, ImportedStatement, IncomeDistributor, OrderSettings, IncomeTotal

from royaltyapp.income.helpers import StatementFactory, find_distinct_matching_errors, process_pending_statements

from .helpers import build_catalog, add_bandcamp_sales, add_order_settings, add_artist_expense, add_bandcamp_errors

def test_can_get_distributors(test_client, db):
    response = test_client.get('/income/distributors')
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0
    assert json.loads(response.data)[0]['distributor_name'] == 'bandcamp'
