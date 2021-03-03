from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal

from sqlalchemy import MetaData, cast, func, exc

def get_income_summary(statement_table, artist_id):

    join_on_track = (
            db.session.query(
                cast((statement_table.c.artist_net), Numeric(8, 2)).label('net'),
                statement_table.c.quantity.label('quantity'),
                statement_table.c.transaction_type.label('transaction_type'),
                statement_table.c.medium.label('medium'),
                TrackCatalogTable.c.catalog_id.label('catalog_id')
                )
                .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
                .filter(statement_table.c.artist_id == artist_id)
            )

    join_on_version = (
        db.session.query(
            cast((statement_table.c.artist_net), Numeric(8, 2)).label('net'),
            statement_table.c.quantity.label('quantity'),
            statement_table.c.transaction_type.label('transaction_type'),
            statement_table.c.medium.label('medium'),
            Version.catalog_id.label('catalog_id')
            )
            .join(Version, statement_table.c.version_id == Version.id)
            .filter(statement_table.c.artist_id == artist_id)
        )

    joined_table = join_on_track.union_all(join_on_version).subquery()

    statement_detail = (
                db.session.query(
                    cast(func.sum(joined_table.c.net), Numeric(8, 2)).label('net'),
                    Catalog.catalog_name.label('catalog_name'),
                    func.sum(joined_table.c.quantity.label('quantity')),
                    joined_table.c.transaction_type.label('transaction_type'),
                    joined_table.c.medium.label('medium'),
                )
                .join(Catalog, joined_table.c.catalog_id == Catalog.id)
                .group_by(
                    Catalog.catalog_name,
                    joined_table.c.transaction_type,
                    joined_table.c.medium,
                    )
            )


    """Income"""
    combined_sales = statement_detail.filter(joined_table.c.transaction_type == 'income').subquery()
    physical_sales = statement_detail.filter(joined_table.c.medium == 'physical').subquery()
    digital_sales = statement_detail.filter(joined_table.c.medium == 'digital').subquery()
    master_sales = statement_detail.filter(joined_table.c.medium == 'master').subquery()

    artist_income = (
                db.session.query(
                    combined_sales.c.catalog_name,
                    func.coalesce(func.sum(combined_sales.c.net), 0).label('combined_net'),
                    func.coalesce(physical_sales.c.net, 0).label('physical_net'),
                    func.coalesce(master_sales.c.net, 0).label('master_net'),
                    func.coalesce(digital_sales.c.net, 0).label('digital_net'))
                    .outerjoin(physical_sales, combined_sales.c.catalog_name == physical_sales.c.catalog_name)
                    .outerjoin(digital_sales, combined_sales.c.catalog_name == digital_sales.c.catalog_name)
                    .outerjoin(master_sales, combined_sales.c.catalog_name == master_sales.c.catalog_name)
                    .group_by(
                        combined_sales.c.catalog_name,
                        func.coalesce(physical_sales.c.net, 0).label('physical_net'),
                        func.coalesce(master_sales.c.net, 0).label('master_net'),
                        func.coalesce(digital_sales.c.net, 0).label('digital_net'))
                ).all()

    return artist_income

def get_expense_detail(statement_table, artist_id):

    expenses = (
            db.session.query(
                statement_table,
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

def get_album_sales_detail(statement_table, artist_id):
    income_detail = (
        db.session.query(
        cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net'),
        Catalog.catalog_name.label('catalog_name'),
        Version.version_number.label('version_number'),
        Version.format.label('format'),
        func.sum(statement_table.c.quantity).label('quantity'),
    )
    .join(Version, statement_table.c.version_id == Version.id)
    .join(Catalog, Version.catalog_id == Catalog.id)
    .group_by(Catalog.catalog_name, Version.version_number, Version.format)
    .filter(statement_table.c.artist_id == artist_id)
    .order_by(Catalog.catalog_name)
    )

    album_sales_detail = (income_detail.filter(statement_table.c.type == 'album')
        .filter(statement_table.c.transaction_type == 'income').all())

    return album_sales_detail

def get_track_sales_detail(statement_table, artist_id):
    income_track_detail = (
        db.session.query(
        cast(func.sum(statement_table.c.artist_net), Numeric(8, 2)).label('net'),
        Track.track_name.label('track_name'),
        func.sum(statement_table.c.quantity).label('quantity'),
        )
        .join(Track, statement_table.c.track_id == Track.id)
        .group_by(Track.track_name)
        .filter(statement_table.c.artist_id == artist_id)
    )

    track_sales_detail = (
            income_track_detail
            .filter(statement_table.c.type != 'album')
            .filter(statement_table.c.medium != 'master')
        .filter(statement_table.c.transaction_type == 'income').all())

    return track_sales_detail

def get_master_sales_detail(statement_table, artist_id):
    income_master_detail = (
        db.session.query(
            cast((statement_table.c.artist_net), Numeric(8, 2)).label('net'),
            Track.track_name.label('track_name'),
            statement_table.c.notes.label('notes'),
        )
            .join(Track, statement_table.c.track_id == Track.id)
            .filter(statement_table.c.artist_id == artist_id)
    )

    master_sales_detail = (income_master_detail.filter(statement_table.c.medium == 'master')
        .filter(statement_table.c.transaction_type == 'income').all())

    return master_sales_detail
