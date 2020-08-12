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

def create_statement_previous_balance_subquery(statement_id):
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

    total_previous_balance = db.session.query(previous_balance_table).subquery()
    
    return total_previous_balance

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
