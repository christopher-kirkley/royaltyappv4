from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, StatementBalanceGenerated, Version, Catalog, StatementBalance, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal

from sqlalchemy import MetaData, cast, func, exc

def get_income_summary(statement_table, artist_id):
    statement_detail = (
        db.session.query(
        cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net'),
        Catalog.catalog_name.label('catalog_name'),
        func.sum(statement_table.c.quantity.label('quantity')),
        )
        .join(Version, statement_table.c.version_id == Version.id)
        .join(Catalog, Version.catalog_id == Catalog.id)
        .group_by(Catalog.catalog_name)
        .filter(statement_table.c.artist_id == artist_id)
        )

    """Income"""
    combined_sales = statement_detail.filter(statement_table.c.transaction_type == 'income').subquery()
    physical_sales = statement_detail.filter(statement_table.c.medium == 'physical').subquery()
    digital_sales = statement_detail.filter(statement_table.c.medium == 'digital').subquery()

    artist_income = (
                db.session.query(
                    combined_sales.c.catalog_name,
                    func.coalesce(combined_sales.c.net, 0).label('combined_net'),
                    func.coalesce(physical_sales.c.net, 0).label('physical_net'),
                    func.coalesce(digital_sales.c.net, 0).label('digital_net'))
                    .outerjoin(physical_sales, combined_sales.c.catalog_name == physical_sales.c.catalog_name)
                    .outerjoin(digital_sales, combined_sales.c.catalog_name == digital_sales.c.catalog_name)
                ).all()

    return artist_income

def get_expense_detail(statement_table, artist_id):
    expenses = (db.session.query(statement_table,
        cast(statement_table.c.artist_net, Numeric(8, 2)).label('artist_net'))
        .filter(statement_table.c.artist_id == artist_id)
        .filter(statement_table.c.expense_type_id == 2)
        .order_by(statement_table.c.date)
    ).all()

    
    return expenses

def get_advance_detail(statement_table, artist_id):
    advances = (db.session.query(
        statement_table,
        cast(statement_table.c.artist_net, Numeric(8, 2)).label('artist_net'))
        .filter(statement_table.c.artist_id == artist_id)
        .filter(statement_table.c.expense_type_id == 1)
        .order_by(statement_table.c.date)).all()
    
    return advances

