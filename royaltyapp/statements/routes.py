from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric

import pandas as pd
import json

from royaltyapp.models import db, StatementBalanceGenerated, StatementBalanceGeneratedSchema, StatementGenerated, StatementGeneratedSchema, Artist, ArtistSchema

from royaltyapp.statements.util import generate_statement as ge
from royaltyapp.statements.util import generate_artist_statement as ga
from royaltyapp.statements.util import view_artist_statement as va

statements = Blueprint('statements', __name__)

@statements.route('/statements/view-balances', methods=['GET'])
def get_statements():
    query = db.session.query(
            StatementBalanceGenerated.id,
            StatementBalanceGenerated.statement_balance_name).all()
    statement_balance_generated_schema = StatementBalanceGeneratedSchema(many=True)
    statements = statement_balance_generated_schema.dumps(query)
    return statements

@statements.route('/statements/generate', methods=['POST'])
def generate_statement():
    data = request.get_json(force=True)
    start_date = data['start_date']
    end_date = data['end_date']
    previous_balance_id = data['previous_balance_id']
    date_range = (str(start_date) + '_' + str(end_date)).replace('-', '_')
    table = ge.create_statement_table(date_range)
    table_obj = table.__table__
    statement_index = ge.add_statement_to_index(table)
    statement_balance_table = ge.create_statement_balance_table(table)
    statement_balance_index = ge.add_statement_balance_to_index(statement_balance_table)
    ge.populate_balance_relationship_table(
            statement_index,
            statement_balance_index,
            previous_balance_id)
    artist_catalog_percentage = ge.find_track_percentage()
    artist_total = ge.find_artist_total(start_date, end_date, artist_catalog_percentage)
    ge.insert_into_table(artist_total, table_obj)
    expense_total = ge.find_expense_total(start_date, end_date, artist_catalog_percentage)
    ge.insert_expense_into_total(expense_total, table_obj)

    return json.dumps({'success': 'true'})

@statements.route('/statements/view', methods=['GET'])
def get_generated_statements():
    query = db.session.query(
            StatementGenerated.id,
            StatementGenerated.statement_name).all()
    statement_generated_schema = StatementGeneratedSchema(many=True)
    statements = statement_generated_schema.dumps(query)
    return statements

@statements.route('/statements/<id>', methods=['GET'])
def statement_detail(id):
    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(1)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(1)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(1)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(1)
    statement_by_artist = ga.create_statement_by_artist_subquery(
                                                        statement_previous_balance_by_artist,
                                                        statement_sales_by_artist,
                                                        statement_advances_by_artist,
                                                        statement_recoupables_by_artist)
    statement_total = (
        db.session.query(
            func.coalesce(
                func.sum(statement_by_artist.c.balance_forward), 0
            )
                .label('total'))
            .filter(statement_by_artist.c.balance_forward > 50)
            .first())

    statement_for_all_artists = (
        db.session.query(Artist, statement_by_artist)
            .join(Artist, Artist.id == statement_by_artist.c.artist_id)
            .all()
    ) 
    
    summary = {
            'statement_total': statement_total.total
            }

    detail = []
    
    for row in statement_for_all_artists:
        obj = {
                'id': row.Artist.id, 
                'artist_name': row.Artist.artist_name,
                'total_previous_balance': row.total_previous_balance,
                'total_sales': row.total_sales,
                'total_recoupable': row.total_recoupable,
                'total_advance': row.total_advance,
                'total_to_split': row.total_to_split,
                'split': row.split,
                'balance_forward': row.balance_forward,
                }
        detail.append(obj)

    json_res = {
            'summary': summary,
            'detail': detail
            }

    return jsonify(json_res)

@statements.route('/statements/<id>/artist/<artist_id>', methods=['GET'])
def statement_detail_artist(id, artist_id):
    table = ga.get_statement_table(id)
    
    income_summary = va.get_income_summary(table, artist_id)
    income = []
    for row in income_summary:
        obj = {
                'catalog_name': row.catalog_name,
                'combined_net': row.combined_net,
                'physical_net': row.physical_net,
                'digital_net': row.digital_net,
                }
        income.append(obj)

    expense_detail = va.get_expense_detail(table, artist_id)
    expense = []
    for row in expense_detail:
        obj = {
                'date': row.date.strftime("%Y-%m-%d"),
                'item': row.item_type,
                'vendor': row.customer,
                'detail': row.description,
                'expense': row.artist_net,
                }
        expense.append(obj)

    advance_detail = va.get_advance_detail(table, artist_id)
    advance = []
    for row in advance_detail:
        obj = {
                'date': row.date.strftime("%Y-%m-%d"),
                'item': row.item_type,
                'vendor': row.customer,
                'detail': row.description,
                'expense': row.artist_net,
                }
        advance.append(obj)
    json_res = {
            'income': income,
            'expense': expense,
            'advance': advance,
            }

    return jsonify(json_res)

