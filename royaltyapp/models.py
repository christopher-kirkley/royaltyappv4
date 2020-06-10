from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String)
    prenom = db.Column(db.String)
    surnom = db.Column(db.String)
    extra = db.Column(db.String)


