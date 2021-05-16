from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from royaltyapp.models import db, ma, add_admin_user
from royaltyapp.cache import cache

import jwt
from flask_jwt_extended import JWTManager

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

    
    with royaltyapp.app_context():
        ma.init_app(royaltyapp)

    return royaltyapp


