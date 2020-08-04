import simplejson

from sqlalchemy import func

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
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

        id = ma.auto_field()
        version_number = ma.auto_field()
        version_name = ma.auto_field()
        upc = ma.auto_field()
        format = ma.auto_field()
    catalog_id = ma.auto_field("catalog") 



class CatalogSchema(ma.SQLAlchemyAutoSchema):
    version = ma.Nested(VersionSchema(many=True))
    artist = ma.Nested("ArtistSchema", exclude=("catalog",))
    tracks = ma.Nested("TrackSchema", many=True)
    

    class Meta:
        model = Catalog
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
    track_id = db.Column(db.Integer)
    version_id = db.Column(db.Integer)
    distributor_id = db.Column(db.Integer)
    statement_id = db.Column(db.Integer)

class IncomePendingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id",
                "distributor",
                "statement",
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


class IncomeDistributor(db.Model):
    __tablename__ = 'income_distributor'
    
    id = db.Column(db.Integer, primary_key=True)
    distributor_name = db.Column(db.String(255), unique=True)
    distributor_statement = db.Column(db.String(255), unique=True)
    income_total = db.relationship('IncomeTotal', backref='income_distributor')
    imported_statement = db.relationship('ImportedStatement',
                                        backref='income_distributor',
                                        passive_deletes=True)

class ImportedStatement(db.Model):
    __tablename__ = 'imported_statement'

    id = db.Column(db.Integer, primary_key=True)
    statement_name = db.Column(db.String(255), unique=True)
    transaction_type = db.Column(db.String(255))

    income_distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'))

    # expense_total = relationship('ExpenseTotal', backref='imported_statement', passive_deletes=True)
    income_total = db.relationship('IncomeTotal', backref='imported_statement', passive_deletes=True)

class ImportedStatementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id",
                "statement_name",
                "income_distributor_id",
                "transaction_type")
        include_relationships = True

class IncomeTotal(db.Model):
    __tablename__ = 'income_total'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Numeric(23, 18))
    label_fee = db.Column(db.Numeric(7, 2))
    label_net = db.Column(db.Numeric(23, 18))
    type = db.Column(db.String(255))
    medium = db.Column(db.String(255))
    customer = db.Column(db.String(255))
    city = db.Column(db.String(255))
    region = db.Column(db.String(255))
    country = db.Column(db.String(255))
    transaction_type = db.Column(db.String(255), default='income')

    imported_statement_id = db.Column(db.Integer, db.ForeignKey('imported_statement.id', ondelete='CASCADE'))
    income_distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'))
    version_id = db.Column(db.Integer, db.ForeignKey('version.id'))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))

class IncomeTotalSchema(ma.SQLAlchemySchema):
    class Meta:
        json_module = simplejson
        fields = (
                "date",
                "quantity",
                "type",
                "medium",
                "version_name",
                "track_name",
                "label_fee",
                "label_net",
                "version_number",
                "amount",
                )
        include_relationships = True
    amount = fields.Decimal()
    label_fee = fields.Decimal()
    label_net = fields.Decimal()


def insert_initial_values(db):
    """Initialize distributor table."""
    statements_to_insert = [
        IncomeDistributor(distributor_statement='bandcamp_statement',
                          distributor_name='bandcamp'),
        IncomeDistributor(distributor_statement='shopify_statement',
                          distributor_name = 'shopify'),
        IncomeDistributor(distributor_statement='sdphysical_statement',
                          distributor_name = 'sdphysical'),
        IncomeDistributor(distributor_statement='sddigital_statement',
                          distributor_name='sddigital'),
        IncomeDistributor(distributor_statement='quickbooks_statement',
                          distributor_name='quickbooks'),
        IncomeDistributor(distributor_statement='sds_statement',
                          distributor_name='sds'),
    ]
    db.session.bulk_save_objects(statements_to_insert)
    db.session.commit()



class OrderSettings(db.Model):
    __tablename__ = 'order_settings'

    id = db.Column(db.Integer, primary_key=True)
    order_percentage = db.Column(db.Float)
    order_fee = db.Column(db.Numeric(8, 2))

    distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'), unique=True)

class OrderSettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "order_percentage", "order_fee", "distributor_id")
        include_relationships = True

class ExpensePending(db.Model):
    __tablename__ = 'expense_pending'

    id = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.String(255))
    date = db.Column(db.Date)
    artist_name = db.Column(db.String(255))
    catalog_number = db.Column(db.String(255))
    vendor = db.Column(db.String(255))
    expense_type = db.Column(db.String(255))
    description = db.Column(db.String(255))
    net = db.Column(db.Numeric(10, 2))
    item_type = db.Column(db.String(255))
    artist_id = db.Column(db.Integer)
    catalog_id = db.Column(db.Integer)
    expense_type_id = db.Column(db.Integer)
    imported_statement_id = db.Column(db.Integer)

class ExpensePendingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id",
                "statement",
                "description")
        include_relationships = True


