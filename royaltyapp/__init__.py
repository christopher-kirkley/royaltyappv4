from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from royaltyapp.models import db, ma, add_admin_user
from royaltyapp.cache import cache

import jwt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

from datetime import datetime
from datetime import timedelta
from datetime import timezone

def create_app(config_class=None):
    royaltyapp = Flask(__name__)
    CORS(royaltyapp, supports_credentials=True)
    
    jwt = JWTManager(royaltyapp)

    royaltyapp.config['CACHE_TYPE']='simple'
    cache.init_app(royaltyapp)

    if config_class==None:
        royaltyapp.config.from_object('config.Config')
    else:
        royaltyapp.config.from_object(config_class)
    
    migrate = Migrate(royaltyapp, db)

    db.init_app(royaltyapp)


    from royaltyapp.home.routes import home
    from royaltyapp.artists.routes import artists
    from royaltyapp.catalog.routes import catalog
    from royaltyapp.bundle.routes import bundle
    from royaltyapp.income.routes import income
    from royaltyapp.expense.routes import expense
    from royaltyapp.statements.routes import statements
    from royaltyapp.settings.routes import settings
    royaltyapp.register_blueprint(home)
    royaltyapp.register_blueprint(artists)
    royaltyapp.register_blueprint(catalog)
    royaltyapp.register_blueprint(bundle)
    royaltyapp.register_blueprint(income)
    royaltyapp.register_blueprint(expense)
    royaltyapp.register_blueprint(statements)
    royaltyapp.register_blueprint(settings)

    @royaltyapp.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            print(exp_timestamp)
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=5))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
                response.set_cookie("session", "true", samesite="Lax", max_age=900)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original respone
            return response

    with royaltyapp.app_context():
        ma.init_app(royaltyapp)

    return royaltyapp

