from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

TrackCatalogTable = db.Table('track_catalog_table',
                    db.Column('track_id', db.Integer, db.ForeignKey('track.id')),
                    db.Column('catalog_id', db.Integer, db.ForeignKey('catalog.id')))

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100))
    prenom = db.Column(db.String)
    surnom = db.Column(db.String)

    catalog = db.relationship('Catalog', backref='artist')
    track = db.relationship('Track', backref='artist')


class Catalog(db.Model):
    __tablename__ = 'catalog'

    id = db.Column(db.Integer, primary_key=True)
    catalog_number = db.Column(db.String(100))
    catalog_name = db.Column(db.String)

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    version = db.relationship('Version', backref='catalog')
    track_catalog = db.relationship("Track",
                                  secondary=TrackCatalogTable,
                                  back_populates="catalog_track")

class Version(db.Model):
    __tablename__ = 'version'

    id = db.Column(db.Integer, primary_key=True)
    upc = db.Column(db.String(30), unique=True)
    version_number = db.Column(db.String(50))
    version_name = db.Column(db.String(30))
    format = db.Column(db.String(30)) 
    
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))

class Track(db.Model):
    __tablename__ = 'track'

    id = db.Column(db.Integer, primary_key=True)
    track_number = db.Column(db.Integer)
    track_name = db.Column(db.String(200))
    isrc = db.Column(db.String(30))

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'))
    catalog_track = db.relationship("Catalog",
                                  secondary=TrackCatalogTable,
                                  back_populates="track_catalog")
    


class TrackSchema(ma.Schema):
    class Meta:
        fields = ('id',
                'track_number',
                'track_name',
                'isrc',
                )
        sqla_session = db.session

class VersionSchema(ma.Schema):
    class Meta:
        fields = ('id',
                'version_number',
                'version_name',
                'upc',
                'format',
                'catalog_id',
                )

class CatalogSchema(ma.Schema):
    version = ma.Nested(VersionSchema(many=True))
    artist = ma.Nested("ArtistSchema", exclude=("catalog",))
    track_catalog = ma.Nested("TrackSchema")

    class Meta:
        fields = ("id",
                "version",
                "catalog_number",
                "catalog_name",
                "artist",
                "track_catalog")

class ArtistSchema(ma.Schema):
    class Meta:
        fields = ("id", "artist_name", "prenom", "surnom", "catalog")
    
    catalog = ma.Nested(CatalogSchema, many=True, only=("id", "catalog_number", "catalog_name", "version"))





