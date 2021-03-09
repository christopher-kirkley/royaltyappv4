from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Table, DECIMAL, Date, Numeric

from royaltyapp.models import db, StatementGenerated, Artist, ImportedStatement, Version, Catalog, Track, TrackCatalogTable, IncomeTotal, ExpenseTotal, BundleVersionTable

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
        notes = db.Column(db.String(255))
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
        track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
        expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'))

    try:
        db.Model.metadata.create_all(bind=db.engine)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"

    return ArtistStatement


def add_statement_to_index(statement_detail_table, statement_summary_table):
    try:
        """Add statement name to table."""
        statement_detail_table = statement_detail_table.__tablename__
        statement_summary_table = statement_summary_table.__tablename__
        statement_generated = StatementGenerated(
                statement_detail_table=statement_detail_table,
                statement_summary_table=statement_summary_table)
        db.session.add(statement_generated)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"
    return statement_generated

def create_statement_balance_table(statement_name):

    class StatementBalanceForward(db.Model):
        __tablename__ = f'{statement_name}_balance'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        # artist_id = db.Column(db.Integer, unique)
        balance_forward = db.Column(db.Numeric(8, 2))
        artist_name = db.Column(db.String(255))

        artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    try:
        db.Model.metadata.create_all(bind=db.engine)
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"

    return StatementBalanceForward

def add_statement_balance_to_index(id, statement_balance_table):
    try:
        statement_generated_obj = db.session.query(StatementGenerated).get(id)
        statement_balance_name = statement_balance_table.__tablename__
        statement_generated_obj.statement_balance_table = statement_balance_name
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        return "already exists"
    return statement_generated_obj

def add_previous_balance_id_to_index(id, previous_balance_id):
    statement_generated_obj = db.session.query(StatementGenerated).get(id)
    statement_generated_obj.previous_balance_id = previous_balance_id
    db.session.commit()

def add_opening_balance_to_index(id):
    statement_generated_obj = db.session.query(StatementGenerated).get(id)
    statement_generated_obj.previous_balance_id = 'opening_balance'
    db.session.commit()

# def populate_balance_relationship_table(statement_index, statement_balance_index, previous_balance_id):
#     statement_index_id = statement_index.id
#     statement_balance_index_id = statement_balance_index.id
#     balance_relationship = StatementBalance(
#                         statement_id=statement_index_id,
#                         current_balance_id=statement_balance_index_id,
#                         previous_balance_id=previous_balance_id)
#     db.session.add(balance_relationship)
#     db.session.commit()

def find_track_percentage():
    """Find percentages of tracks in each catalog."""
    """If item has no tracks, coalesce to 1"""
    """ This could be worth revisiting
    and make the tracks tied to version rather than catalog, but its a big redesign"""

    artist_tracks_per_catalog = (
            db.session.query(
                Track.artist_id,
                TrackCatalogTable.c.catalog_id,
                func.count(TrackCatalogTable.c.track_id).label('track_count')
                )
            .join(Track, Track.id == TrackCatalogTable.c.track_id)
            .group_by(Track.artist_id, TrackCatalogTable.c.catalog_id)
            .subquery())

    tracks_per_catalog = (
            db.session.query(
                func.count(TrackCatalogTable.c.track_id).label('total_track_count'),
                TrackCatalogTable.c.catalog_id
                )
            .group_by(TrackCatalogTable.c.catalog_id)
            .subquery()
            )

    artist_catalog_percentage = (
            db.session.query(
                artist_tracks_per_catalog.c.artist_id,
                artist_tracks_per_catalog.c.catalog_id,
                cast(
                    cast(artist_tracks_per_catalog.c.track_count, DECIMAL(4, 2))
                    /
                    tracks_per_catalog.c.total_track_count, DECIMAL(8, 4)
                    )
                .label('percentage'))
            .join(
                tracks_per_catalog,
                tracks_per_catalog.c.catalog_id == artist_tracks_per_catalog.c.catalog_id
                )
            .subquery()
            )

    return artist_catalog_percentage

def split_bundles_to_versions():

    """ Make IncomeTotal subquery with split bundles into versions """
    count_per_bundle = (db.session.query(BundleVersionTable.c.bundle_id,
                                     func.count(BundleVersionTable.c.bundle_id)
                                     .label('version_count'))
                    .group_by(BundleVersionTable.c.bundle_id)
                    .subquery()
                    )

    sel = (db.session
            .query(
                (IncomeTotal.transaction_type).label('transaction_type'),
                IncomeTotal.date.label('date'),
                IncomeTotal.quantity.label('quantity'),
                (IncomeTotal.label_net / count_per_bundle.c.version_count).label('label_net'),
                IncomeTotal.type.label('type'),
                IncomeTotal.medium.label('medium'),
                IncomeTotal.income_distributor_id.label('income_distributor_id'),
                (BundleVersionTable.c.version_id).label('version_id'),
                IncomeTotal.track_id.label('track_id'),
                IncomeTotal.customer.label('customer'),
                IncomeTotal.notes.label('notes'),
                IncomeTotal.city.label('city'),
                IncomeTotal.region.label('region'),
                IncomeTotal.country.label('country'),
                )
            .join(count_per_bundle, count_per_bundle.c.bundle_id == IncomeTotal.bundle_id)
            .join(BundleVersionTable, BundleVersionTable.c.bundle_id == IncomeTotal.bundle_id)
         )

    """Query for albums, calculate artist total per catalog item."""
    albums = (db.session.query(
            IncomeTotal.transaction_type,
            IncomeTotal.date,
            IncomeTotal.quantity,
            IncomeTotal.label_net,
            IncomeTotal.type,
            IncomeTotal.medium,
            IncomeTotal.income_distributor_id,
            IncomeTotal.version_id,
            IncomeTotal.track_id,
            IncomeTotal.customer,
            IncomeTotal.notes,
            IncomeTotal.city,
            IncomeTotal.region,
            IncomeTotal.country
            )
            .filter(IncomeTotal.bundle_id == None))

    joined = sel.union_all(albums).subquery()
    
    return joined

def find_artist_total(start_date, end_date, artist_catalog_percentage):

    subquery = split_bundles_to_versions()
    
    """Query for albums, calculate artist total per catalog item."""
    sel = (db.session.query(
            subquery.c.transaction_type,
            subquery.c.date,
            subquery.c.quantity,
            (subquery.c.label_net * func.coalesce(artist_catalog_percentage.c.percentage, 1)).label('artist_net'),
            subquery.c.type,
            subquery.c.medium,
            subquery.c.income_distributor_id,
            subquery.c.version_id,
            subquery.c.track_id,
            subquery.c.customer,
            subquery.c.notes,
            subquery.c.city,
            subquery.c.region,
            subquery.c.country,
            func.coalesce(artist_catalog_percentage.c.artist_id, Catalog.artist_id) # this is the problem line, income total not getting artist_id
            ).join(Version, Version.id == subquery.c.version_id)
            .join(Catalog, Catalog.id == Version.catalog_id)
            .filter(subquery.c.date.between(start_date, end_date))
            .filter(subquery.c.type == 'album')
            .filter(subquery.c.medium != 'master'))

    # sel = sel.filter(IncomeTotal.type == 'album')
    # sel = sel.join(Version, Version.id == IncomeTotal.version_id)
    # sel = sel.join(Catalog, Catalog.id == Version.catalog_id)

    artist_total_catalog = sel.outerjoin(artist_catalog_percentage, artist_catalog_percentage.c.catalog_id == Catalog.id)

    """Query for tracks."""
    sel = db.session.query(IncomeTotal.transaction_type,
    IncomeTotal.date,
    IncomeTotal.quantity,
    IncomeTotal.label_net.label('artist_net'),
    IncomeTotal.type,
    IncomeTotal.medium,
    IncomeTotal.income_distributor_id,
    IncomeTotal.version_id,
    IncomeTotal.track_id,
    IncomeTotal.customer,
    IncomeTotal.notes,
    IncomeTotal.city,
    IncomeTotal.region,
    IncomeTotal.country,
    Track.artist_id,
    ).filter(IncomeTotal.date.between(start_date, end_date))
    sel = sel.join(Track, Track.id == IncomeTotal.track_id)
    sel = sel.filter(IncomeTotal.type != 'album')
    artist_total_track = sel.filter(IncomeTotal.medium != 'master')

    """Query for master."""
    sel = (db.session.query(
        IncomeTotal.transaction_type,
        IncomeTotal.date,
        IncomeTotal.quantity,
        IncomeTotal.label_net.label('artist_net'),
        IncomeTotal.type,
        IncomeTotal.medium,
        IncomeTotal.income_distributor_id,
        IncomeTotal.version_id,
        IncomeTotal.track_id,
        IncomeTotal.customer,
        IncomeTotal.notes,
        IncomeTotal.city,
        IncomeTotal.region,
        IncomeTotal.country,
        Track.artist_id,
        )
        .filter(
            IncomeTotal.date.between(start_date, end_date)
            )
        )
    sel = sel.join(Track, Track.id == IncomeTotal.track_id)
    artist_total_master = sel.filter(IncomeTotal.medium == 'master')

    """Union ALL queries, returning Artist Income By Period. Makes a cool subquery that I can use."""

    artist_total = artist_total_catalog.union_all(artist_total_track).union_all(artist_total_master)

    return artist_total

def insert_into_table(artist_total, statement_table):
    """Populate variable table with query result."""
    ins = (statement_table.insert()
            .from_select([
                'transaction_type',
                'date',
                'quantity',
                'artist_net',
                'type',
                'medium',
                'income_distributor_id',
                'version_id',
                'track_id',
                'customer',
                'notes',
                'city',
                'region',
                'country',
                'artist_id',
                ]
    , artist_total))

    db.session.execute(ins)
    db.session.commit()

def find_expense_total(start_date, end_date, artist_catalog_percentage):
    """Total expenses by catalog number, divided over artists."""
    sel = db.session.query(ExpenseTotal.transaction_type,
                           ExpenseTotal.description,
                           (ExpenseTotal.net * artist_catalog_percentage.c.percentage).label('artist_net'),
                           artist_catalog_percentage.c.artist_id,
                           ExpenseTotal.vendor,
                           ExpenseTotal.date,
                           ExpenseTotal.expense_type_id,
                           ExpenseTotal.item_type,
                           ExpenseTotal.catalog_id,
                           )
    sel = sel.filter(ExpenseTotal.date.between(start_date, end_date))
    expense_by_catalog = sel.join(artist_catalog_percentage,
                                    artist_catalog_percentage.c.catalog_id == ExpenseTotal.catalog_id)

    """Query for items by artist id."""
    sel = db.session.query(ExpenseTotal.transaction_type,
                           ExpenseTotal.description,
                           ExpenseTotal.net.label('artist_net'),
                           ExpenseTotal.artist_id,
                           ExpenseTotal.vendor,
                           ExpenseTotal.date,
                           ExpenseTotal.expense_type_id,
                           ExpenseTotal.item_type,
                           ExpenseTotal.catalog_id,
                           )
    sel = sel.filter(ExpenseTotal.date.between(start_date, end_date))
    expense_by_artist = sel.filter(ExpenseTotal.catalog_id == None)

    """Union queries."""

    artist_expense_total = expense_by_catalog.union(expense_by_artist)

    return artist_expense_total

def insert_expense_into_total(expense_total, statement_table):
    """Populate variable table with query result."""
    ins = (
            statement_table.insert().from_select(['transaction_type',
                                  'description',
                                  'artist_net',
                                  'artist_id',
                                  'customer',
                                  'date',
                                  'expense_type_id',
                                  'item_type',
                                  'catalog_id',
                                  ]
                                 , expense_total))
    db.session.execute(ins)
    db.session.commit()



# def create_empty_balance_table():
#     check_statement_none = (db.session.query(StatementBalanceGenerated)
#             .filter(StatementBalanceGenerated.statement_balance_name == 'statement_balance_none')
#             .all())

#     if len(check_statement_none) == 0:
#         create_statement_balance_table('none')
#         db.Model.metadata.create_all(bind=db.engine)
#         statement_balance_generated = StatementBalanceGenerated(statement_balance_name='statement_balance_none')
#         db.session.add(statement_balance_generated)
#         db.session.commit()

