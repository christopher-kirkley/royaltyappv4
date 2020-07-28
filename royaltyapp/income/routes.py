from flask import Blueprint, jsonify, request
from sqlalchemy import exc
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema

from .helpers import StatementFactory, find_distinct_matching_errors

income = Blueprint('income', __name__)

@income.route('/income/import-sales', methods=['POST'])
def import_sales():
    file = request.files['file']
    filename = file.filename
    statement_source = request.form['statement_source']
    statement = StatementFactory.get_statement(file, statement_source)
    statement.create_df()
    statement.clean()
    statement.modify_columns()
    statement.insert_to_db()
    return jsonify({'success': 'true'})

@income.route('/income/matching-errors', methods=['GET'])
def get_matching_errors():
    query = find_distinct_matching_errors().all()
    income_pendings_schema = IncomePendingSchema(many=True)
    matching_errors = income_pendings_schema.dumps(query)
    return matching_errors

@income.route('/income/update-errors', methods=['PUT'])
def update_errors():
    data = request.get_json(force=True)
    try:
        sel = find_distinct_matching_errors()
        for item in data['data_to_match']:
            if item.get('version_number'):
                sel = sel.filter(IncomePending.version_number == item['version_number'])
            if item.get('album_name'):
                sel = sel.filter(IncomePending.album_name == item['album_name'])
            if item.get('medium'):
                sel = sel.filter(IncomePending.medium == item['medium'])
            if item.get('description'):
                sel = sel.filter(IncomePending.medium == item['description'])
        temp = sel.subquery()
        (db.session.query(IncomePending)
            .filter(IncomePending.id == temp.c.id)
            .update({IncomePending.upc_id : data['upc_id']}))
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

