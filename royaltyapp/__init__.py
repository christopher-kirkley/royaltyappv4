from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from royaltyapp.models import db


def create_app(config_class=None):
    royaltyapp = Flask(__name__)
    if config_class==None:
        royaltyapp.config.from_object('config.Config')
    else:
        royaltyapp.config.from_object(config_class)
    
    db.init_app(royaltyapp)

    from royaltyapp.home.routes import home
    royaltyapp.register_blueprint(home)
    
    with royaltyapp.app_context():
        db.create_all()

    return royaltyapp
