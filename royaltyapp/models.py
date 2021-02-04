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

BundleVersionTable = db.Table('bundle_version_table',
        db.Column('bundle_id', db.Integer, db.ForeignKey('bundle.id')),
        db.Column('version_id', db.Integer, db.ForeignKey('version.id'))
                           )
class Bundle(db.Model):
    """Bundle, containing multiple versions."""

    __tablename__ = 'bundle'
    id = db.Column(db.Integer, primary_key=True)
    bundle_number = db.Column(db.String(50), unique=True)
    bundle_name = db.Column(db.String(30))

    version_bundle = db.relationship("Version",
            secondary=BundleVersionTable,
            back_populates="bundle_version")


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

    bundle_version = db.relationship("Bundle",
            secondary=BundleVersionTable,
            back_populates="version_bundle")


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




class BundleSchema(ma.SQLAlchemyAutoSchema):

    version_bundle = ma.Nested(VersionSchema(many=True))

    class Meta:
        model = Bundle
        fields = ("id", "bundle_number", "bundle_name", "version_bundle"
                )

    def _custom_serializer(self, obj):
        return 'adfas'

        



# try to refactor to make this a temp table using ORM core
class PendingCatalog(db.Model):
    __tablename__ = 'pending_catalog'

    id = db.Column(db.Integer, primary_key=True)
    catalog_number = db.Column(db.String(255))
    catalog_name = db.Column(db.String(255))
    catalog_artist = db.Column(db.String(255))

class PendingTrack(db.Model):
    __tablename__ = 'pending_track'

    id = db.Column(db.Integer, primary_key=True)
    isrc = db.Column(db.String(255))
    track_artist = db.Column(db.String(255))
    track_name = db.Column(db.String(255))
    track_number = db.Column(db.Integer)
    catalog_number = db.Column(db.String(255))

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
    """Table populated with all available income sources. Should rename to income_source"""
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
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    income_distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'))

    # expense_total = relationship('ExpenseTotal', backref='imported_statement', passive_deletes=True)
    income_total = db.relationship('IncomeTotal', backref='imported_statement', passive_deletes=True)

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

class IncomeDistributorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
                "id",
                "distributor_name",
                "distributor_statement"
                )
        include_relationships = True

class ImportedStatementSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        fields = (
                "id",
                "statement_name",
                "income_distributor_id",
                "transaction_type",
                "start_date",
                "end_date",
                )


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


class OrderSettings(db.Model):
    __tablename__ = 'order_settings'

    id = db.Column(db.Integer, primary_key=True)
    order_percentage = db.Column(db.Float)
    order_fee = db.Column(db.Numeric(8, 2))
    order_limit = db.Column(db.Numeric(8, 2))

    distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'), unique=True)

class OrderSettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        json_module = simplejson
        fields = ("id",
                "order_percentage",
                "order_fee",
                "distributor_id",
                "distributor")
        include_relationships = True
    order_percentage = fields.Decimal()
    order_fee = fields.Decimal()
    distributor = ma.Nested(IncomeDistributorSchema(many=True))

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
        json_module = simplejson
        fields = ("id",
                "statement",
                "date",
                "net",
                "catalog_id",
                "catalog_number",
                "artist_name",
                "artist_id",
                "expense_type",
                "item_type",
                "vendor",
                "description")
        include_relationships = True
    net = fields.Decimal()


class ExpenseType(db.Model):
    __tablename__ = 'expense_type'

    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(255), unique=True)

    # expense_total = db.relationship('ExpenseTotal', backref='expense_type', passive_deletes=True)


class ExpenseTotal(db.Model):
    __tablename__ = 'expense_total'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    vendor = db.Column(db.String(255))
    description = db.Column(db.String(255))
    net = db.Column(db.Numeric(10, 2))
    item_type = db.Column(db.String(255))
    transaction_type = db.Column(db.String(255), default='expense')

    imported_statement_id = db.Column(db.Integer, db.ForeignKey('imported_statement.id', ondelete='CASCADE'))
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    artist = db.relationship(Artist, primaryjoin=artist_id == Artist.id)
    catalog = db.relationship(Catalog, primaryjoin=catalog_id == Catalog.id)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'))

class ExpenseTotalSchema(ma.SQLAlchemyAutoSchema):
    artist = ma.Nested("ArtistSchema", exclude=('catalog','prenom', 'surnom'))
    catalog = ma.Nested("CatalogSchema", exclude=('artist', 'tracks', 'version'))
    
    class Meta:
        json_module = simplejson
        fields = (
                "id",
                "date",
                "catalog",
                "artist",
                "vendor",
                "description",
                "net",
                "item_type",
                "transaction_type",
                )
        include_relationships = True
    net = fields.Decimal()

class StatementGenerated(db.Model):
    __tablename__ = 'statement_generated'

    id = db.Column(db.Integer, primary_key=True)
    statement_detail_table = db.Column(db.String(255), unique=True)
    statement_summary_table = db.Column(db.String(255), unique=True)
    statement_balance_table = db.Column(db.String(255), unique=True)
    previous_balance_id = db.Column(db.Integer)

class StatementGeneratedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
                "id",
                "statement_detail_table",
                "statement_summary_table",
                "statement_balance_table",
                "previous_balance_id",
                )

class StatementBalanceNone(db.Model):
    __tablename__ = 'statement_balance_none'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(255))
    balance_forward = db.Column(db.Numeric(8, 2))


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
        ExpenseType(id=1,
                    expense_type='advance'),
        ExpenseType(id=2,
                    expense_type='recoupable'),
        OrderSettings(
            distributor_id='1',
            order_fee='0',
            order_percentage='0',
            order_limit='0',
            ),
        OrderSettings(
            distributor_id='2',
            order_fee='0',
            order_percentage='0',
            order_limit='0',
            ),
        OrderSettings(
            distributor_id='3',
            order_fee='0',
            order_percentage='0',
            order_limit='0',
            ),
        OrderSettings(
            distributor_id='4',
            order_fee='0',
            order_percentage='0',
            order_limit='0',
            ),
        OrderSettings(
            distributor_id='5',
            order_fee='0',
            order_percentage='0',
            order_limit='0',
            ),
    ]
    db.session.bulk_save_objects(statements_to_insert)
    db.session.commit()
