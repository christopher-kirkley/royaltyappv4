from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from sqlalchemy.schema import Table

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal

from sqlalchemy import MetaData, cast, func, exc

from datetime import datetime

def get_statement_table(statement_id, metadata):
    print('get_statement')
    start_time = datetime.now()

    statement_detail_table = (
        db.session.query(StatementGenerated.statement_detail_table)
        .filter(StatementGenerated.id == statement_id)
        .first()
        ).statement_detail_table

    table = Table(statement_detail_table, metadata, autoload=True, autoload_with=db.engine)
    # table = metadata.tables.get(statement_detail_table)
    db.session.commit()

    end_time = datetime.now()
    print(end_time - start_time)

    return table


def lookup_statement_summary_table(statement_id, metadata):
    print('lookup_statement_summary_table')
    start_time = datetime.now()

    statement_name = (
        db.session.query(StatementGenerated.statement_summary_table)
        .filter(StatementGenerated.id == statement_id)
        .first()
        ).statement_summary_table
    table = metadata.tables.get(statement_name)
    db.session.commit()

    end_time = datetime.now()
    print(end_time - start_time)

    return table


def create_statement_previous_balance_by_artist_subquery(statement_id, metadata):
    print('create_statement_previous_balance')
    start_time = datetime.now()

    previous_balance_id = (db.session.query(StatementGenerated.previous_balance_id)
                           .filter(StatementGenerated.id == statement_id)
                           .first()
                           ).previous_balance_id

    if previous_balance_id == 0:
        previous_balance_name = 'statement_balance_none'
    else:
        previous_balance_name = (db.session.query(StatementGenerated)
                              .filter(StatementGenerated.id == previous_balance_id)
                              .first()
                              ).statement_balance_table

    previous_balance_table = metadata.tables.get(previous_balance_name)

    previous_balance_by_artist = (
            db.session.query(
                previous_balance_table.c.artist_id.label('artist_id'),
                cast(func.sum(previous_balance_table.c.balance_forward), Numeric(8, 2)).label('balance_forward')
            )
            .group_by(previous_balance_table.c.artist_id)
            .subquery())

    end_time = datetime.now()
    print(end_time - start_time)

    return previous_balance_by_artist

def create_statement_sales_by_artist_subquery(statement_id, metadata):
    print('create_statement_sales')
    start_time = datetime.now()

    statement_table = get_statement_table(statement_id, metadata)
    statement_sales_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
                         cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net')
                         )
            .filter(statement_table.c.transaction_type == 'income')
            .group_by(statement_table.c.artist_id)
            .subquery()
    )

    end_time = datetime.now()
    print(end_time - start_time)

    return statement_sales_by_artist

def create_statement_advances_by_artist_subquery(statement_id, metadata):
    print('create_statement_advances')
    start_time = datetime.now()

    statement_table = get_statement_table(statement_id, metadata)
    statement_advances_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
                         cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net')
                         )
            .filter(statement_table.c.expense_type_id == 1)
            .group_by(statement_table.c.artist_id)
            .subquery()
    )

    end_time = datetime.now()
    print(end_time - start_time)

    return statement_advances_by_artist

def create_statement_recoupables_by_artist_subquery(statement_id, metadata):
    print('create_statement_sales')
    start_time = datetime.now()

    statement_table = get_statement_table(statement_id, metadata)
    statement_recoupables_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
        cast(func.sum(
        statement_table.c.artist_net), Numeric(8, 2)).label('net')
        )
        .filter(statement_table.c.expense_type_id == 2)
        .group_by(statement_table.c.artist_id)
        .subquery()
    )

    end_time = datetime.now()
    print(end_time - start_time)

    return statement_recoupables_by_artist

def create_statement_summary_table(date_range):

    class StatementSummary(db.Model):

        __tablename__ = f'statement_summary_{date_range}'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        previous_balance = db.Column(db.Numeric(8, 2))
        recoupables = db.Column(db.Numeric(8, 2))
        sales = db.Column(db.Numeric(8, 2))
        advances = db.Column(db.Numeric(8, 2))

        artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    try:
        db.Model.metadata.create_all(bind=db.engine)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"

    return StatementSummary

def create_statement_by_artist_subquery(
        statement_previous_balance_by_artist,
        statement_sales_by_artist,
        statement_advances_by_artist,
        statement_recoupables_by_artist,
        ):

    print('create_statement_by_artist_sub')
    start_time = datetime.now()

    sel = (
        db.session.query(Artist.id.label('artist_id'),
                         func.coalesce(statement_previous_balance_by_artist.c.balance_forward, 0).label('statement_previous_balance_by_artist'),
                         func.coalesce(statement_recoupables_by_artist.c.net, 0).label('statement_recoupables_by_artist'),
                         func.coalesce(statement_sales_by_artist.c.net, 0).label('statement_sales_by_artist'),
                         func.coalesce(statement_advances_by_artist.c.net, 0).label('statement_advances_by_artist'),
                         )
            .outerjoin(statement_previous_balance_by_artist, statement_previous_balance_by_artist.c.artist_id == Artist.id)
            .outerjoin(statement_advances_by_artist, statement_advances_by_artist.c.artist_id == Artist.id)
            .outerjoin(statement_recoupables_by_artist, statement_recoupables_by_artist.c.artist_id == Artist.id)
            .outerjoin(statement_sales_by_artist, statement_sales_by_artist.c.artist_id == Artist.id)
    )

    end_time = datetime.now()
    print(end_time - start_time)

    return sel


def insert_into_statement_summary(
        statement_by_artist,
        statement_summary_table
        ):

    print('insert_into_statement')
    start_time = datetime.now()

    ins = (
            statement_summary_table.insert().from_select([
                'artist_id',
                'previous_balance',
                'recoupables',
                'sales',
                'advances',
              ], statement_by_artist))

    db.session.execute(ins)
    db.session.commit()

    end_time = datetime.now()
    print(end_time - start_time)
    
    return True

def insert_into_balance_table(statement_id, metadata): 

    print('insert_into_balance')
    start_time = datetime.now()

    statement_index = db.session.query(StatementGenerated).filter(StatementGenerated.id == statement_id).first()

    # lookup balance statement
    statement_balance_table = metadata.tables.get(statement_index.statement_balance_table)
    statement_summary_table = metadata.tables.get(statement_index.statement_summary_table)

    entries_to_delete = statement_balance_table.delete()
    db.session.execute(entries_to_delete)
    db.session.commit()

    sel = db.session.query(
            statement_summary_table.c.artist_id,
            statement_summary_table.c.previous_balance + (statement_summary_table.c.sales - statement_summary_table.c.recoupables)/2 - statement_summary_table.c.advances)
    ins = (statement_balance_table
           .insert().from_select(['artist_id',
                                  'balance_forward'],
                                 sel)
           )

    db.session.execute(ins)
    db.session.commit()

    end_time = datetime.now()
    print(end_time - start_time)
    
