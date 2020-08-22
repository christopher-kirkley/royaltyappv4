
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, Version, Catalog

from sqlalchemy import MetaData, cast, func, exc


def define_artist_statement_table(date_range):

    class ArtistStatement(db.Model):

        """Currently exists as a model for statement income, but needs to be a combined statement
        All artists transactions over date range, that can be used to generate individual statements.

        Need a column to specify if income or expense and type of expense (recoupable vs advance)"""

        __tablename__ = f'statement_{date_range}'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        transaction_type = db.Column(db.String(255)) # income of expense
        description = db.Column(db.String(255)) # transaction description
        quantity = db.Column(db.Integer)
        artist_net = db.Column(Numeric(23, 18))
        customer = db.Column(db.String(255))
        city = db.Column(db.String(255))
        region = db.Column(db.String(255))
        country = db.Column(db.String(255))
        type = db.Column(db.String(255))
        medium = db.Column(db.String(255))
        date = db.Column(Date)
        item_type = db.Column(db.String(255))

        artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
        catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
        income_distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'))
        version_id = db.Column(db.Integer, db.ForeignKey('version.id'))
        tracks_id = db.Column(db.Integer, db.ForeignKey('track.id'))
        expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'))

    return ArtistStatement

