from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric, Date
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd
import json

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema, ImportedStatement, ImportedStatementSchema, IncomeTotal, IncomeTotalSchema, IncomeDistributor, IncomeDistributorSchema

from .helpers import StatementFactory, find_distinct_version_matching_errors, find_distinct_track_matching_errors

from .util import process_income as pi


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
    query = find_distinct_version_matching_errors().all()
    income_pendings_schema = IncomePendingSchema(many=True)
    matching_errors = income_pendings_schema.dumps(query)
    return matching_errors

@income.route('/income/track-matching-errors', methods=['GET'])
def get_track_matching_errors():
    query = find_distinct_track_matching_errors().all()
    income_pendings_schema = IncomePendingSchema(many=True)
    matching_errors = income_pendings_schema.dumps(query)
    return matching_errors

@income.route('/income/update-track-errors', methods=['PUT'])
def update_track_errors():
    data = request.get_json(force=True)
    try:
        sel = find_distinct_track_matching_errors()
        for item in data['data_to_match']:
            if item.get('isrc_id'):
                sel = sel.filter(IncomePending.isrc_id == item['isrc_id'])
            if item.get('version_number'):
                sel = sel.filter(IncomePending.version_number == item['version_number'])
            if item.get('album_name'):
                sel = sel.filter(IncomePending.album_name == item['album_name'])
            if item.get('medium'):
                sel = sel.filter(IncomePending.medium == item['medium'])
            if item.get('description'):
                sel = sel.filter(IncomePending.description == item['description'])
            if item.get('catalog_id'):
                sel = sel.filter(IncomePending.catalog_id == item['catalog_id'])
            if item.get('distributor'):
                sel = sel.filter(IncomePending.distributor == item['distributor'])
            if item.get('upc_id'):
                sel = sel.filter(IncomePending.upc_id == item['upc_id'])
            if item.get('type'):
                sel = sel.filter(IncomePending.type == item['type'])
        temp = sel.subquery()
        updated_errors = len(db.session.query(IncomePending).filter(IncomePending.id == temp.c.id).all())
        (db.session.query(IncomePending)
            .filter(IncomePending.id == temp.c.id)
            .update({IncomePending.isrc_id : data['isrc_id']}))
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'updated': updated_errors})

@income.route('/income/update-errors', methods=['PUT'])
def update_errors():
    data = request.get_json(force=True)
    try:
        sel = find_distinct_version_matching_errors()
        for item in data['data_to_match']:
            if item.get('version_number'):
                sel = sel.filter(IncomePending.version_number == item['version_number'])
            if item.get('album_name'):
                sel = sel.filter(IncomePending.album_name == item['album_name'])
            if item.get('medium'):
                sel = sel.filter(IncomePending.medium == item['medium'])
            if item.get('description'):
                sel = sel.filter(IncomePending.description == item['description'])
            if item.get('catalog_id'):
                sel = sel.filter(IncomePending.catalog_id == item['catalog_id'])
            if item.get('distributor'):
                sel = sel.filter(IncomePending.distributor == item['distributor'])
            if item.get('upc_id'):
                sel = sel.filter(IncomePending.upc_id == item['upc_id'])
            if item.get('type'):
                sel = sel.filter(IncomePending.type == item['type'])
        temp = sel.subquery()
        updated_errors = len(db.session.query(IncomePending).filter(IncomePending.id == temp.c.id).all())
        (db.session.query(IncomePending)
            .filter(IncomePending.id == temp.c.id)
            .update({IncomePending.upc_id : data['upc_id']}))
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'updated': updated_errors})

@income.route('/income/pending-statements', methods=['GET'])
def get_pending_statements():
    query = db.session.query(IncomePending.statement, IncomePending.distributor).distinct(IncomePending.statement).all()
    income_pendings_schema = IncomePendingSchema(many=True)
    pending_statements = income_pendings_schema.dumps(query)
    return pending_statements

@income.route('/income/pending-statements/<name>', methods=['DELETE'])
def delete_pending_statements(name):
    res = (db.session.query(IncomePending)
            .filter(IncomePending.statement==name))
    res.delete()
    db.session.commit()
    return jsonify({'success': 'true'})

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

@income.route('/income/process-pending', methods=['POST'])
def process_pending_income():
    pi.normalize_distributor()
    pi.normalize_version()
    pi.normalize_track()
    pi.insert_into_imported_statements()
    pi.normalize_statement_id()
    pi.calculate_adjusted_amount()
    pi.move_from_pending_income_to_total()
    return jsonify({'success': 'true'})

@income.route('/income/imported-statements', methods=['GET'])
def get_imported_statements():
    query = (db.session.query(
        ImportedStatement.income_distributor_id,
        IncomeDistributor.distributor_name,
        )
            .join(IncomeDistributor)
            .filter(ImportedStatement.transaction_type == 'income')
            .all())
    res = []
    for distributor in query:
        entry = {}
        data = (db.session.query(
            ImportedStatement.id,
            ImportedStatement.statement_name,
            ImportedStatement.start_date,
            ImportedStatement.end_date,
            )
                .filter(ImportedStatement.transaction_type == 'income')
                .filter(ImportedStatement.income_distributor_id == distributor.income_distributor_id)
                .all())

        for row in data:
            obj = {
                    'start_date': row.start_date.strftime("%Y-%m-%d"),
                    'end_date': row.end_date.strftime("%Y-%m-%d"),
                    'id': row.id,
                    'statement_name': row.statement_name
                    }
            entry[distributor.distributor_name] = obj
            res.append(entry)




    return jsonify(res)

@income.route('/income/statements/<id>', methods=['GET'])
def get_imported_statement_detail(id):
    income_total_schema = IncomeTotalSchema(many=True)

    number_of_records = (db.session.query(func.count(IncomeTotal.id).label('count')).filter(IncomeTotal.imported_statement_id == id).first()).count

    total_income = (db.session.query(cast(func.sum(IncomeTotal.label_net), Numeric(8, 2)).label('label_net'), cast(func.sum(IncomeTotal.amount), Numeric(8, 2)).label('amount'), cast(func.sum(IncomeTotal.label_fee), Numeric(8, 2)).label('label_fee')).filter(IncomeTotal.imported_statement_id == id)
                    .first())

    total_income_res = income_total_schema.dumps(total_income)

    versions_sold = (db.session.query
            (func.sum(IncomeTotal.amount).label('amount'),
            func.sum(IncomeTotal.quantity).label('quantity'),
            Version.version_number)
    .join(Version, IncomeTotal.version_id == Version.id)
    .filter(IncomeTotal.imported_statement_id == id)
    .group_by(Version.version_number)
    )
    physical_versions = versions_sold.filter(IncomeTotal.medium == 'physical').all()
    digital_versions = versions_sold.filter(IncomeTotal.medium == 'digital').all()

    digital_versions_res = income_total_schema.dumps(digital_versions)
    physical_versions_res = income_total_schema.dumps(physical_versions)
 

    query = db.session.query(IncomeTotal).filter(IncomeTotal.imported_statement_id == id).all()
    statement_detail = income_total_schema.dumps(query)

    return jsonify([{'number_of_records': number_of_records,
                    'amount': total_income.amount,
                    'label_fee': total_income.label_fee,
                    'label_net': total_income.label_net,
                    'data': json.loads(statement_detail),
                    'digital': json.loads(digital_versions_res),
                    'physical': json.loads(physical_versions_res)
                    }])

@income.route('/income/statements/<id>', methods=['DELETE'])
def delete_income_statement(id):
    i = ImportedStatement.__table__.delete().where(ImportedStatement.id == id)
    db.session.execute(i)
    db.session.commit()
    return jsonify({'success': 'true'})

@income.route('/income/distributors', methods=['GET'])
def get_distributors():
    query = db.session.query(IncomeDistributor).all()
    distributor_schema = IncomeDistributorSchema(many=True)
    distributors = distributor_schema.dumps(query)
    return distributors

    return jsonify({'success': 'true'})

