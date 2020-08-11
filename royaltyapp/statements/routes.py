from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric

import pandas as pd
import json

from royaltyapp.models import db, StatementBalanceGenerated, StatementBalanceGeneratedSchema

statements = Blueprint('statements', __name__)

@statements.route('/statements/view', methods=['GET'])
def get_statements():
    query = db.session.query(
            StatementBalanceGenerated.id,
            StatementBalanceGenerated.statement_balance_name).all()
    statement_balance_generated_schema = StatementBalanceGeneratedSchema(many=True)
    statements = statement_balance_generated_schema.dumps(query)
    return statements

@statements.route('/statements/generate', methods=['POST'])
def generate_statement():
    return json.dumps({'success': 'true'})
