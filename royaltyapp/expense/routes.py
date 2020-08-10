from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd
import json

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema, ImportedStatement, ImportedStatementSchema, IncomeTotal, IncomeTotalSchema, ExpensePending, ExpensePendingSchema

from .helpers import expense_matching_errors, artist_matching_errors, catalog_matching_errors, expense_type_matching_errors

from .util import process_expense as pe

expense = Blueprint('expense', __name__)

@expense.route('/expense/import-statement', methods=['POST'])
def import_statement():
    file = request.files['file']
    filename = file.filename
    df = pd.read_csv(file)
    df['statement'] = file.filename
    columns_for_expense = [
            'statement',
            'date',
            'artist_name',
            'catalog_number',
            'vendor',
            'expense_type',
            'description',
            'net',
            'item_type',
            'artist_id',
            'catalog_id',
            'expense_type_id',
            'imported_statement_id',
        ]
    df.reindex(columns=columns_for_expense)
    df.to_sql('expense_pending', con=db.engine, if_exists='append', index=False)
    return jsonify({'success': 'true'})

@expense.route('/expense/pending-statements', methods=['GET'])
def get_pending_statements():
    query = db.session.query(ExpensePending.statement).distinct(ExpensePending.statement).all()
    expense_pending_schema = ExpensePendingSchema(many=True)
    pending_statements = expense_pending_schema.dumps(query)
    return pending_statements

@expense.route('/expense/matching-errors', methods=['GET'])
def get_matching_errors():
    query = artist_matching_errors()
    expense_pending_schema = ExpensePendingSchema(many=True)
    artist_errors = expense_pending_schema.dumps(query)
    query = catalog_matching_errors()
    catalog_errors = expense_pending_schema.dumps(query)
    query = expense_type_matching_errors()
    type_errors = expense_pending_schema.dumps(query)
    return jsonify([{
                    'total_matching_errors': 2,
                    'artist_matching_errors': json.loads(artist_errors),
                    'catalog_matching_errors': json.loads(catalog_errors),
                    'type_matching_errors': json.loads(type_errors)
                    }])
    return matching_errors

@expense.route('/expense/update-errors', methods=['PUT'])
def update_errors():
    data = request.get_json(force=True)
    try:
        for item in data['data_to_match']:
            if item.get('artist_name'):
                sel = artist_matching_errors()
                sel = sel.filter(ExpensePending.artist_name == item['artist_name'])
                temp = sel.subquery()
                (db.session.query(ExpensePending)
                    .filter(ExpensePending.id == temp.c.id)
                    .update({ExpensePending.artist_name : data['artist_name']}))
            if item.get('catalog_number'):
                sel = catalog_matching_errors()
                sel = sel.filter(ExpensePending.catalog_number == item['catalog_number'])
                temp = sel.subquery()
                (db.session.query(ExpensePending)
                    .filter(ExpensePending.id == temp.c.id)
                    .update({ExpensePending.catalog_number : data['catalog_number']}))
            if item.get('id'):
                sel = db.session.query(ExpensePending).filter(ExpensePending.id==item['id'])
                sel.update({ExpensePending.expense_type : data['expense_type']})
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@expense.route('/expense/process-pending', methods=['POST'])
def process_pending():
    pe.normalize_artist()
    pe.normalize_catalog()
    pe.normalize_expense_type()
    pe.insert_into_imported_statements()
    pe.normalize_statement_id()
    pe.move_from_pending_expense_to_total()
    return jsonify({'success': 'true'})

@expense.route('/expense/imported-statements', methods=['GET'])
def get_imported_statements():
    query = db.session.query(ImportedStatement).all()
    imported_statement_schema = ImportedStatementSchema(many=True)
    statements = imported_statement_schema.dumps(query)
    return statements
