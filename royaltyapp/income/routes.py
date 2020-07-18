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
    sel = db.session.query(IncomePending, Version)
    sel = sel.outerjoin(Version, Version.upc == IncomePending.upc_id)
    # sel = sel.outerjoin(Bundle, Bundle.bundle_number == IncomePending.version_number)
    sel = sel.filter(Version.upc == None).order_by(IncomePending.catalog_id).all()

    query = find_distinct_matching_errors().all()
    income_pendings_schema = IncomePendingSchema(many=True)
    matching_errors = income_pendings_schema.dumps(query)

    return matching_errors

