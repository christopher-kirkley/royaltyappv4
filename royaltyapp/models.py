from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100))
    prenom = db.Column(db.String)
    surnom = db.Column(db.String)

class Catalog(db.Model):
    __tablename__ = 'catalog'

    id = db.Column(db.Integer, primary_key=True)
    catalog_number = db.Column(db.String(100))
    catalog_name = db.Column(db.String)
    artist_id = db.Column(db.Integer)

