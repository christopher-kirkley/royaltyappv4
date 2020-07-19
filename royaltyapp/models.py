from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine

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
    tracks = db.relationship("Track",
                                  secondary=TrackCatalogTable,
                                  back_populates="catalog")


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
    catalog = db.relationship("Catalog",
                                  secondary=TrackCatalogTable,
                                  back_populates="tracks")
    



class TrackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = 'Track'
        fields = ('track_number',
                'track_name',
                'isrc',
                'artist_id',
                'id'
                )

class VersionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Version
        # include_relationships = True

        id = ma.auto_field()
        version_number = ma.auto_field()
        version_name = ma.auto_field()
        upc = ma.auto_field()
        format = ma.auto_field()
        # catalog = ma.auto_field("catalog_id", dump_only=True)
    catalog_id = ma.auto_field("catalog") 

        # fields = ('id',
        #         'version_number',
        #         'version_name',
        #         'upc',
        #         'format',
        #         'catalog_id',
        #         )


class CatalogSchema(ma.SQLAlchemyAutoSchema):
    version = ma.Nested(VersionSchema(many=True))
    artist = ma.Nested("ArtistSchema", exclude=("catalog",))
    tracks = ma.Nested("TrackSchema", many=True)
    

    class Meta:
        model = Catalog
        # include_relationships = True

        # id = ma.auto_field()
      # catalog_name = ma.auto_field()
        # catalog_number = ma.auto_field()
        fields = ("id",
                "version",
                "catalog_number",
                "catalog_name",
                "tracks",
                "artist"
                )

    def _custom_serializer(self, obj):
        return 'adfas'


class ArtistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "artist_name", "prenom", "surnom", "catalog")
        include_relationships = True
    
    catalog = ma.Nested(CatalogSchema, many=True, only=("id", "catalog_number", "catalog_name", "version"))





# try to refactor to make this a temp table using ORM core
class Pending(db.Model):
    __tablename__ = 'pending'

    id = db.Column(db.Integer, primary_key=True)
    isrc = db.Column(db.String(255))
    track_artist = db.Column(db.String(255))
    track_name = db.Column(db.String(255))
    track_number = db.Column(db.Integer)
    catalog_number = db.Column(db.String(255))
    catalog_name = db.Column(db.String(255))
    catalog_artist = db.Column(db.String(255))


class PendingVersion(db.Model):
    __tablename__ = 'pending_version'

    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(255))
    version_name = db.Column(db.String(255))
    upc = db.Column(db.String(255))
    format = db.Column(db.String(255))
    catalog_number = db.Column(db.String(255))


class IncomePending(db.Model):
    __tablename__ = 'income_pending'

    id = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.String(255))
    distributor = db.Column(db.String(255))
    date = db.Column(db.Date)
    order_id = db.Column(db.String(255))
    upc_id = db.Column(db.String(255))
    isrc_id = db.Column(db.String(255))
    version_number = db.Column(db.String(255))
    catalog_id = db.Column(db.String(255))
    album_name = db.Column(db.String(255))
    track_name = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Numeric(23, 18))
    label_fee = db.Column(db.Numeric(8, 2))
    label_net = db.Column(db.Numeric(23, 8))
    customer = db.Column(db.String(255))
    city = db.Column(db.String(255))
    region = db.Column(db.String(255))
    country = db.Column(db.String(255))
    type = db.Column(db.String(255))
    medium = db.Column(db.String(255))
    product = db.Column(db.String(255))
    description = db.Column(db.String(255))
    tracks_id = db.Column(db.Integer)
    version_id = db.Column(db.Integer)
    distributor_id = db.Column(db.Integer)
    statement_id = db.Column(db.Integer)

class IncomePendingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id",
                "distributor",
                "isrc_id",
                "upc_id",
                "version_number",
                "catalog_id",
                "album_name",
                "track_name",
                "type",
                "medium",
                "description")
        include_relationships = True

# class IncomeDistributor(db.Model):
#     __tablename__ = 'income_distributor'
#     id = Column(Integer, primary_key=True)
#     distributor_name = Column(String(255), unique=True)
#     distributor_statement = Column(String(255), unique=True)

#     income_total = relationship('IncomeTotal', backref='income_distributor')
#     imported_statement = relationship('ImportedStatement', backref='income_distributor', passive_deletes=True)

