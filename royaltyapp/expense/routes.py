from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric
# from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
#         VersionSchema, Track, TrackCatalogTable

import pandas as pd
import json

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema, ImportedStatement, ImportedStatementSchema, IncomeTotal, IncomeTotalSchema, ExpensePending, ExpensePendingSchema

from .helpers import expense_matching_errors

# from .util import process_income as pi

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
    query = expense_matching_errors()
    expense_pending_schema = ExpensePendingSchema(many=True)
    matching_errors = expense_pending_schema.dumps(query)
    return matching_errors

# @income.route('/income/update-errors', methods=['PUT'])
# def update_errors():
#     data = request.get_json(force=True)
#     try:
#         sel = find_distinct_matching_errors()
#         for item in data['data_to_match']:
#             if item.get('version_number'):
#                 sel = sel.filter(IncomePending.version_number == item['version_number'])
#             if item.get('album_name'):
#                 sel = sel.filter(IncomePending.album_name == item['album_name'])
#             if item.get('medium'):
#                 sel = sel.filter(IncomePending.medium == item['medium'])
#             if item.get('description'):
#                 sel = sel.filter(IncomePending.medium == item['description'])
#         temp = sel.subquery()
#         (db.session.query(IncomePending)
#             .filter(IncomePending.id == temp.c.id)
#             .update({IncomePending.upc_id : data['upc_id']}))
#         db.session.commit()
#     except exc.DataError:
#         db.session.rollback()
#         return jsonify({'success': 'false'})
#     return jsonify({'success': 'true'})


# @income.route('/income/order-settings', methods=['GET'])
# def get_order_fees():
#     query = db.session.query(OrderSettings).all()
#     order_settings_schema = OrderSettingsSchema(many=True)
#     settings = order_settings_schema.dumps(query)
#     return settings
    
# @income.route('/income/order-settings', methods=['POST'])
# def add_order_fees():
#     data = request.get_json(force=True)
#     new_order_setting = OrderSettings(
#             distributor_id = data['distributor_id'],
#             order_percentage = data['order_percentage'],
#             order_fee = data['order_fee']
#             )
#     db.session.add(new_order_setting)
#     db.session.commit()
#     return jsonify({'success': 'true'})

# @income.route('/income/order-settings', methods=['PUT'])
# def edit_order_fee():
#     data = request.get_json(force=True)
#     distributor_id = data['distributor_id']
#     res = db.session.query(OrderSettings).filter(OrderSettings.distributor_id == distributor_id).first()
#     if res == None:
#         return jsonify({'success': 'false'})
#     id = res.id
#     order_setting = db.session.query(OrderSettings).get(id)
#     order_setting.order_percentage = data['order_percentage']
#     order_setting.order_fee = data['order_fee']
#     db.session.commit()
#     return jsonify({'success': 'true'})

# @income.route('/income/process-pending', methods=['POST'])
# def process_pending_income():
#     pi.normalize_distributor()
#     pi.normalize_version()
#     pi.normalize_track()
#     pi.insert_into_imported_statements()
#     pi.normalize_statement_id()
#     pi.calculate_adjusted_amount()
#     pi.move_from_pending_income_to_total()
#     return jsonify({'success': 'true'})

# @income.route('/income/imported-statements', methods=['GET'])
# def get_imported_statements():
#     query = db.session.query(ImportedStatement).all()
#     imported_statement_schema = ImportedStatementSchema(many=True)
#     statements = imported_statement_schema.dumps(query)
#     return statements

# @income.route('/income/statements/<id>', methods=['GET'])
# def get_imported_statement_detail(id):
#     income_total_schema = IncomeTotalSchema(many=True)

#     number_of_records = (db.session.query(func.count(IncomeTotal.id).label('count')).filter(IncomeTotal.imported_statement_id == id).first()).count

#     total_income = (db.session.query(cast(func.sum(IncomeTotal.label_net), Numeric(8, 2)).label('label_net'), cast(func.sum(IncomeTotal.amount), Numeric(8, 2)).label('amount'), cast(func.sum(IncomeTotal.label_fee), Numeric(8, 2)).label('label_fee')).filter(IncomeTotal.imported_statement_id == id)
#                     .first())

#     total_income_res = income_total_schema.dumps(total_income)

#     versions_sold = (db.session.query
#             (func.sum(IncomeTotal.amount).label('amount'),
#             func.sum(IncomeTotal.quantity).label('quantity'),
#             Version.version_number)
#     .join(Version, IncomeTotal.version_id == Version.id)
#     .filter(IncomeTotal.imported_statement_id == id)
#     .group_by(Version.version_number)
#     )
#     physical_versions = versions_sold.filter(IncomeTotal.medium == 'physical').all()
#     digital_versions = versions_sold.filter(IncomeTotal.medium == 'digital').all()

#     digital_versions_res = income_total_schema.dumps(digital_versions)
#     physical_versions_res = income_total_schema.dumps(physical_versions)
 

#     query = db.session.query(IncomeTotal).filter(IncomeTotal.imported_statement_id == id).all()
#     statement_detail = income_total_schema.dumps(query)

#     return jsonify([{'number_of_records': number_of_records,
#                     'amount': total_income.amount,
#                     'label_fee': total_income.label_fee,
#                     'label_net': total_income.label_net,
#                     'data': json.loads(statement_detail),
#                     'digital': json.loads(digital_versions_res),
#                     'physical': json.loads(physical_versions_res)
#                     }])

# @income.route('/income/statements/<id>', methods=['DELETE'])
# def delete_income_statement(id):
#     i = ImportedStatement.__table__.delete().where(ImportedStatement.id == id)
#     db.session.execute(i)
#     db.session.commit()
#     return jsonify({'success': 'true'})

