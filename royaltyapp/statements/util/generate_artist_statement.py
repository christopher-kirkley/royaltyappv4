from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, StatementBalanceGenerated, Version, Catalog, StatementBalance, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal

from sqlalchemy import MetaData, cast, func, exc

def get_statement_table(statement_id):
    statement_name = (
        db.session.query(StatementGenerated.statement_name)
        .filter(StatementGenerated.id == statement_id)
        .first()
        ).statement_name
    metadata = MetaData(db.engine, reflect=True)
    table = metadata.tables.get(statement_name)
    db.session.commit()
    return table

def create_statement_previous_balance_by_artist_subquery(statement_id):
    previous_balance_id = (db.session.query(StatementBalance.previous_balance_id)
                           .filter(StatementBalance.statement_id == statement_id)
                           .first()
                           ).previous_balance_id

    previous_balance_name = (db.session.query(StatementBalanceGenerated)
                              .filter(StatementBalanceGenerated.id == previous_balance_id)
                              .first()
                              ).statement_balance_name

    metadata = MetaData(db.engine, reflect=True)

    previous_balance_table = metadata.tables.get(previous_balance_name)

    previous_balance_by_artist = db.session.query(previous_balance_table).subquery()
    
    return previous_balance_by_artist

def create_statement_sales_by_artist_subquery(statement_id):
    statement_table = get_statement_table(statement_id)
    statement_sales_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
                         cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net')
                         )
            .filter(statement_table.c.transaction_type == 'income')
            .group_by(statement_table.c.artist_id)
            .subquery()
    )
    return statement_sales_by_artist

def create_statement_advances_by_artist_subquery(statement_id):
    statement_table = get_statement_table(statement_id)
    statement_advances_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
                         cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net')
                         )
            .filter(statement_table.c.expense_type_id == 1)
            .group_by(statement_table.c.artist_id)
            .subquery()
    )
    return statement_advances_by_artist

def create_statement_recoupables_by_artist_subquery(statement_id):
    statement_table = get_statement_table(statement_id)
    statement_recoupables_by_artist = (
        db.session.query(statement_table.c.artist_id.label('artist_id'),
        cast(func.sum(
        statement_table.c.artist_net), Numeric(8, 2)).label('net')
        )
        .filter(statement_table.c.expense_type_id == 2)
        .group_by(statement_table.c.artist_id)
        .subquery()
    )
    return statement_recoupables_by_artist

def create_statement_by_artist_subquery(
        statement_previous_balance_by_artist,
        statement_sales_by_artist,
        statement_advances_by_artist,
        statement_recoupables_by_artist,
        ):

    sel = (
        db.session.query(Artist.id.label('artist_id'),
                         func.coalesce(statement_previous_balance_by_artist.c.balance_forward, 0).label('statement_previous_balance_by_artist'),
                         func.coalesce(statement_recoupables_by_artist.c.net, 0).label('statement_recoupables_by_artist'),
                         func.coalesce(statement_sales_by_artist.c.net, 0).label('statement_sales_by_artist'),
                         func.coalesce(statement_advances_by_artist.c.net, 0).label('statement_advances_by_artist'),
                         )
            .outerjoin(statement_previous_balance_by_artist, statement_previous_balance_by_artist.c.id == Artist.id)
            .outerjoin(statement_advances_by_artist, statement_advances_by_artist.c.artist_id == Artist.id)
            .outerjoin(statement_recoupables_by_artist, statement_recoupables_by_artist.c.artist_id == Artist.id)
            .outerjoin(statement_sales_by_artist, statement_sales_by_artist.c.artist_id == Artist.id)
            .subquery()
    )

    statement_for_all_artists = (
        db.session.query(sel.c.artist_id,
                         sel.c.statement_previous_balance_by_artist.label('total_previous_balance'),
                         sel.c.statement_sales_by_artist.label('total_sales'),
                         sel.c.statement_recoupables_by_artist.label('total_recoupable'),
                         sel.c.statement_advances_by_artist.label('total_advance'),
                         (sel.c.statement_sales_by_artist - sel.c.statement_recoupables_by_artist).label('total_to_split'),
                         cast(
                             ((sel.c.statement_sales_by_artist - sel.c.statement_recoupables_by_artist)/2),
                             Numeric(8, 2))
                         .label('split'),
                         cast(
                             ((sel.c.statement_sales_by_artist - sel.c.statement_recoupables_by_artist)/2 - sel.c.statement_advances_by_artist + sel.c.statement_previous_balance_by_artist),
                             Numeric(8, 2))
                         .label('balance_forward')
                         )
    )

    statement = statement_for_all_artists.subquery()
    db.session.commit()
    
    return statement

