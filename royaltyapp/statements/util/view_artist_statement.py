from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal

from sqlalchemy import MetaData, cast, func, exc, or_

from datetime import datetime

def get_income_summary(statement_table, artist_id):

    start_time = datetime.now()

    statement_table = (
            db.session.query(statement_table).filter(statement_table.c.artist_id == artist_id)).subquery()

    join_master = (
            db.session.query(
                statement_table.c.artist_net.label('net'),
                statement_table.c.quantity.label('quantity'),
                statement_table.c.type.label('type'),
                statement_table.c.medium.label('medium'),
                TrackCatalogTable.c.catalog_id.label('catalog_id')
                )
            .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
                .filter(statement_table.c.artist_id == artist_id)
                .filter(statement_table.c.medium == 'master')
            )

    join_track = (
            db.session.query(
                statement_table.c.artist_net.label('net'),
                statement_table.c.quantity.label('quantity'),
                statement_table.c.type.label('type'),
                statement_table.c.medium.label('medium'),
                TrackCatalogTable.c.catalog_id.label('catalog_id')
                )
                .join(TrackCatalogTable, TrackCatalogTable.c.track_id == statement_table.c.track_id)
                .filter(or_(
                        statement_table.c.type != 'album',
                        statement_table.c.type !='master')
                        )
                .filter(statement_table.c.medium == 'digital')
            )

    join_version = (
        db.session.query(
            statement_table.c.artist_net.label('net'),
            statement_table.c.quantity.label('quantity'),
            statement_table.c.type.label('type'),
            statement_table.c.medium.label('medium'),
            Version.catalog_id.label('catalog_id')
            )
            .join(Version, statement_table.c.version_id == Version.id)
            .filter(statement_table.c.type == 'album')
        )

    joined_table = join_master.union_all(join_version, join_track).subquery()

    """ Sum net by catalog id"""
    sum_by_catalog_name = (
                db.session.query(
                    func.sum(joined_table.c.net).label('net'),
                    func.sum(joined_table.c.quantity).label('quantity'),
                    Catalog.catalog_name,
                    joined_table.c.medium.label('medium'),
                )
                .join(Catalog, joined_table.c.catalog_id == Catalog.id)
                .group_by(
                    Catalog.catalog_name,
                    joined_table.c.medium,
                    )
            ).subquery()


    query = db.session.query(
            sum_by_catalog_name.c.catalog_name.distinct()).all()

    catalog_names = [item for t in query for item in t]

    summary = []

    for catalog_name in catalog_names:

        combined_sales = (
                db.session.query(
                    func.coalesce(
                        cast(func.sum(sum_by_catalog_name.c.net), Numeric(8, 2)), 0)
                    )
                .filter(sum_by_catalog_name.c.catalog_name == catalog_name)
                .one())[0]

        digital_sales = (
                db.session.query(
                    func.coalesce(
                        cast(func.sum(sum_by_catalog_name.c.net), Numeric(8,2))
                        , 0)
                    )
                .filter(sum_by_catalog_name.c.catalog_name == catalog_name)
                .filter(sum_by_catalog_name.c.medium == 'digital')
                .one())[0]

        master_sales = (
                db.session.query(
                    func.coalesce(
                        cast(func.sum(sum_by_catalog_name.c.net), Numeric(8,2))
                        , 0)
                    )
                .filter(sum_by_catalog_name.c.catalog_name == catalog_name)
                .filter(sum_by_catalog_name.c.medium == 'master')
                .one())[0]

        physical_sales = (
                db.session.query(
                    func.coalesce(
                        cast(func.sum(sum_by_catalog_name.c.net), Numeric(8,2))
                        , 0)
                    )
                .filter(sum_by_catalog_name.c.catalog_name == catalog_name)
                .filter(sum_by_catalog_name.c.medium == 'physical')
                .one())[0]

        summary.append(
                {
                'catalog_name': catalog_name,
                'combined_net': combined_sales,
                'digital_net': digital_sales,
                'physical_net': physical_sales,
                'master_net': master_sales,
                })

    end_time = datetime.now()
    print(f'get income summary: {end_time - start_time}')

    return summary

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
