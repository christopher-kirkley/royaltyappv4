from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric, extract
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd
import json
import datetime

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema, ImportedStatement, ImportedStatementSchema, IncomeTotal, IncomeTotalSchema, ExpensePending, ExpensePendingSchema, ExpenseTotalSchema, ExpenseTotal

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

@expense.route('/expense/artist-matching-errors', methods=['GET'])
def get_artist_matching_errors():
    query = artist_matching_errors()
    expense_pending_schema = ExpensePendingSchema(many=True)
    artist_errors = expense_pending_schema.dumps(query)
    return artist_errors

@expense.route('/expense/catalog-matching-errors', methods=['GET'])
def get_catalog_matching_errors():
    query = catalog_matching_errors()
    expense_pending_schema = ExpensePendingSchema(many=True)
    catalog_errors = expense_pending_schema.dumps(query)
    return catalog_errors

@expense.route('/expense/type-matching-errors', methods=['GET'])
def get_type_matching_errors():
    query = expense_type_matching_errors()
    expense_pending_schema = ExpensePendingSchema(many=True)
    type_errors = expense_pending_schema.dumps(query)
    return type_errors

@expense.route('/expense/match-errors', methods=['PUT'])
def match_errors():
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
    # query = (db.session.query(ImportedStatement)
    #         .filter(ImportedStatement.transaction_type == 'expense')
    #         .all()
    #         )
    # imported_statement_schema = ImportedStatementSchema(many=True)
    # statements = imported_statement_schema.dumps(query)
    # return statements
    result = {}


    query = (
            db.session.query(
                ImportedStatement.start_date
                )
            .filter(ImportedStatement.transaction_type == 'expense')
            .all())

    for row in query:
        result[row.start_date.strftime("%Y")] = []


    for year in result:
        data = (db.session.query(
            ImportedStatement.id,
            ImportedStatement.statement_name,
            ImportedStatement.start_date,
            ImportedStatement.end_date,
            )
                .filter(ImportedStatement.transaction_type == 'expense')
                .filter(extract('year', ImportedStatement.start_date) == year)
                .all())

        for item in data:
            obj = {
                    'start_date': item.start_date.strftime("%Y-%m-%d"),
                    'end_date': item.end_date.strftime("%Y-%m-%d"),
                    'id': item.id,
                    'statement_name': item.statement_name
                    }
            result[year].append(obj)

    return jsonify(result)


@expense.route('/expense/statements/<id>', methods=['GET'])
def get_imported_statement_detail(id):
    expense_total_schema = ExpenseTotalSchema(many=True)

    number_of_records = (db.session.query(func.count(ExpenseTotal.id).label('count')).filter(ExpenseTotal.imported_statement_id == id).first()).count
 
    query = db.session.query(ExpenseTotal).filter(ExpenseTotal.imported_statement_id == id).all()
    statement_detail = expense_total_schema.dumps(query)

    return jsonify([{'number_of_records': number_of_records,
                    'data': json.loads(statement_detail),
                    }])

@expense.route('/expense/statements/<id>', methods=['DELETE'])
def delete_expense_statement(id):
    i = ImportedStatement.__table__.delete().where(ImportedStatement.id == id)
    db.session.execute(i)
    db.session.commit()
    return jsonify({'success': 'true'})

@expense.route('/expense/update-errors', methods=['PUT'])
def update_errors():
    data = request.get_json(force=True)
    try:
        for id in data['selected_ids']:
            obj = db.session.query(ExpensePending).get(id)
            if data['error_type'] == 'artist':
                obj.artist_name = data['new_value']
                db.session.commit()
            if data['error_type'] == 'type':
                obj.expense_type = data['new_value']
                db.session.commit()
            if data['error_type'] == 'catalog':
                obj.catalog_number = data['new_value']
                db.session.commit()
            
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})


