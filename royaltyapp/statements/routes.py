from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric

import pandas as pd
import json

from royaltyapp.models import db, StatementBalanceGenerated, StatementBalanceGeneratedSchema, StatementGenerated, StatementGeneratedSchema

from royaltyapp.statements.util import generate_statement as ge

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
    statement_index = ge.add_statement_to_index(table)
    statement_balance_table = ge.create_statement_balance_table(table)
    statement_balance_index = ge.add_statement_balance_to_index(statement_balance_table)
    ge.populate_balance_relationship_table(
            statement_index,
            statement_balance_index,
            previous_balance_id)
    return json.dumps({'success': 'true'})

@statements.route('/statements/view', methods=['GET'])
def get_generated_statements():
    query = db.session.query(
            StatementGenerated.id,
            StatementGenerated.statement_name).all()
    statement_generated_schema = StatementGeneratedSchema(many=True)
    statements = statement_generated_schema.dumps(query)
    return statements

