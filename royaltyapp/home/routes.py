from flask import Blueprint, jsonify, request, Response, make_response
from sqlalchemy import exc, func, cast, Numeric, Date

from royaltyapp.models import db, User

import pandas as pd
import json

home = Blueprint('home', __name__)

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

@home.route('/login', methods=['POST'])
def login():

    data = request.get_json(force=True)

    if not data or not data['email'] or not data['password']:
        return make_response('Could not verify', 401)

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return make_response('Could not verify', 402)

    if data['password'] == user.password:
        response = jsonify({"msg": "login successful"})
        access_token = create_access_token(identity=data['email'])
        set_access_cookies(response, access_token)
        response.set_cookie("session", "true", samesite="Lax", max_age=60)
        return response

    return jsonify({'sucess': 'false'})
