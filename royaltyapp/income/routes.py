from flask import Blueprint, jsonify, request
from sqlalchemy import exc
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema

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

@income.route('/income/pending-statements', methods=['GET'])
def get_pending_statements():
    query = db.session.query(IncomePending.statement, IncomePending.distributor).distinct(IncomePending.statement).all()
    income_pendings_schema = IncomePendingSchema(many=True)
    pending_statements = income_pendings_schema.dumps(query)
    return pending_statements

@income.route('/income/order-settings', methods=['GET'])
def get_order_fees():
    query = db.session.query(OrderSettings).all()
    order_settings_schema = OrderSettingsSchema(many=True)
    settings = order_settings_schema.dumps(query)
    return settings
    
@income.route('/income/order-settings', methods=['POST'])
def add_order_fees():
    data = request.get_json(force=True)
    new_order_setting = OrderSettings(
            distributor_id = data['distributor_id'],
            order_percentage = data['order_percentage'],
            order_fee = data['order_fee']
            )
    db.session.add(new_order_setting)
    db.session.commit()
    return jsonify({'success': 'true'})

@income.route('/income/order-settings', methods=['PUT'])
def edit_order_fee():
    data = request.get_json(force=True)
    distributor_id = data['distributor_id']
    res = db.session.query(OrderSettings).filter(OrderSettings.distributor_id == distributor_id).first()
    if res == None:
        return jsonify({'success': 'false'})
    id = res.id
    order_setting = db.session.query(OrderSettings).get(id)
    order_setting.order_percentage = data['order_percentage']
    order_setting.order_fee = data['order_fee']
    db.session.commit()
    return jsonify({'success': 'true'})


