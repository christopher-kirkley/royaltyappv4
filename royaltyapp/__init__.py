from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from royaltyapp.models import db, ma




def create_app(config_class=None):
    royaltyapp = Flask(__name__)
    CORS(royaltyapp)
    
    if config_class==None:
        royaltyapp.config.from_object('config.Config')
    else:
        royaltyapp.config.from_object(config_class)
    
    db.init_app(royaltyapp)

    from royaltyapp.home.routes import home
    from royaltyapp.artists.routes import artists
    from royaltyapp.catalog.routes import catalog
    from royaltyapp.income.routes import income
    from royaltyapp.expense.routes import expense
    royaltyapp.register_blueprint(home)
    royaltyapp.register_blueprint(artists)
    royaltyapp.register_blueprint(catalog)
    royaltyapp.register_blueprint(income)
    royaltyapp.register_blueprint(expense)

    
    with royaltyapp.app_context():
        ma.init_app(royaltyapp)

    return royaltyapp


