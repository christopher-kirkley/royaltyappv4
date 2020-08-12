import pytest
import json
import datetime

import os
import io

import pandas as pd
import numpy as np

from decimal import Decimal

import time

from royaltyapp.models import StatementGenerated, StatementBalanceGenerated, StatementBalance, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, IncomePending

from royaltyapp.statements.helpers import define_artist_statement_table

from royaltyapp.statements.util import generate_artist_statement as ga

from .helpers import build_catalog, add_artist_expense, add_order_settings, add_catalog_expense, add_bandcamp_sales, add_processed_income, add_processed_expense, generate_statement, setup_test1, setup_statement


def test_can_find_statement_table(test_client, db):
    setup_statement(test_client, db)
    table = ga.get_statement_table(1)
    assert table.name == 'statement_2020_01_01_2020_01_31'

def test_can_get_statement_previous_balance_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    assert db.session.query(statement_previous_balance_by_artist).all() == []

def test_can_get_statement_sales_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    assert db.session.query(statement_sales_by_artist).all() == [(1, Decimal('24.95'))]

def test_can_get_statement_advances_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    assert db.session.query(statement_advances_by_artist).all() == [
            (1, Decimal('9542.63')),
            (None, Decimal('1078.46'))
            ]

def test_can_get_statement_recoupables_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    assert db.session.query(statement_recoupables_by_artist).all() == [
            (1, Decimal('1398.06')),
            ]

def test_can_get_statement_by_artist_subquery(test_client, db):
    setup_statement(test_client, db)
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    statement_by_artist = ga.create_statement_by_artist_subquery(
                                                        statement_previous_balance_by_artist,
                                                        statement_sales_by_artist,
                                                        statement_advances_by_artist,
                                                        statement_recoupables_by_artist)
    assert len(db.session.query(statement_by_artist).all()) > 0
    assert db.session.query(statement_by_artist).all() == [
            (
                1, # artist_id
                Decimal('0'), # previous_balance 
                Decimal('24.95'), # sales 
                Decimal('1398.06'), # recoupable
                Decimal('9542.63'), # advance
                Decimal('-1373.11'), # total to split
                Decimal('-686.56'), # sales - recoupable / 2
                Decimal('-10229.19'), # balance forward
                )]
