from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, StatementBalanceGenerated, Version, Catalog, StatementBalance

from sqlalchemy import MetaData, cast, func, exc

def create_statement_table(date_range):

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

        # artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
        # catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
        # income_distributor_id = db.Column(db.Integer, db.ForeignKey('income_distributor.id'))
        # version_id = db.Column(db.Integer, db.ForeignKey('version.id'))
        # tracks_id = db.Column(db.Integer, db.ForeignKey('track.id'))
        # expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'))

    try:
        db.Model.metadata.create_all(bind=db.engine)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"

    return ArtistStatement

def add_statement_to_index(statement_table):
    try:
        """Add statement name to table."""
        statement_name = statement_table.__tablename__
        statement_generated = StatementGenerated(statement_name=statement_name)
        db.session.add(statement_generated)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"
    return statement_generated

def create_statement_balance_table(statement_table):

    statement_name = statement_table.__tablename__

    class StatementBalance(db.Model):
        __tablename__ = f'{statement_name}_balance'
        __table_args__ = {'extend_existing': True}
        id = Column(db.Integer, primary_key=True)
        artist_name = db.Column(db.String(255))
        balance_forward = db.Column(db.Numeric(8, 2))

        # artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    try:
        db.Model.metadata.create_all(bind=db.engine)
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"

    return StatementBalance

def add_statement_balance_to_index(statement_balance_table):
    try:
        statement_balance_name = statement_balance_table.__tablename__
        statement_balance_generated = StatementBalanceGenerated(statement_balance_name=statement_balance_name)
        db.session.add(statement_balance_generated)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"
    return statement_balance_generated

def populate_balance_relationship_table(statement_index, statement_balance_index, previous_balance_id):
    statement_index_id = statement_index.id
    statement_balance_index_id = statement_balance_index.id
    balance_relationship = StatementBalance(
                        statement_id=statement_index_id,
                        current_balance_id=statement_balance_index_id,
                        previous_balance_id=previous_balance_id)
    db.session.add(balance_relationship)
    db.session.commit()

