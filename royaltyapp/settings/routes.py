from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric, Date

import pandas as pd
import json

from royaltyapp.models import db, IncomePending, Version, IncomePendingSchema, OrderSettings, OrderSettingsSchema, ImportedStatement, ImportedStatementSchema, IncomeTotal, IncomeTotalSchema, IncomeDistributor, IncomeDistributorSchema

settings = Blueprint('settings', __name__)

@settings.route('/settings/order-fee', methods=['GET'])
def get_order_fees():
    query = (db.session.query(
        OrderSettings.distributor_id,
        OrderSettings.order_fee,
        OrderSettings.order_percentage,
        OrderSettings.order_limit,
        IncomeDistributor.distributor_name)
            .join(IncomeDistributor,
                IncomeDistributor.id == OrderSettings.distributor_id)
            .all())
    return jsonify(query)
 
@settings.route('/settings/order-fee', methods=['POST'])
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

@settings.route('/settings/order-fee', methods=['PUT'])
def update_order_setting():
    data = request.get_json(force=True)
    for item in data:
        distributor_id = item['distributor_id']
        res = db.session.query(OrderSettings).filter(OrderSettings.distributor_id == distributor_id).first()
        if res == None:
            return jsonify({'success': 'false'})
        id = res.id
        order_setting = db.session.query(OrderSettings).get(id)
        order_setting.order_percentage = item['order_percentage']
        order_setting.order_fee = item['order_fee']
        db.session.commit()
    return jsonify({'success': 'true'})

