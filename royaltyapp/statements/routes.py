from flask import Blueprint, jsonify, request
from sqlalchemy import exc, func, cast, Numeric, MetaData

import pandas as pd
import json

from royaltyapp.models import db, StatementGenerated, StatementGeneratedSchema, Artist, ArtistSchema, Version, Catalog  

from royaltyapp.statements.util import generate_statement as ge
from royaltyapp.statements.util import generate_artist_statement as ga
from royaltyapp.statements.util import view_artist_statement as va

statements = Blueprint('statements', __name__)

@statements.route('/statements/view-balances', methods=['GET'])
def get_statements():
    query = db.session.query(
            StatementGenerated.id,
            StatementGenerated.statement_balance_table).all()
    statement_generated_schema = StatementGeneratedSchema(many=True)
    statements = statement_generated_schema.dumps(query)
    return statements

@statements.route('/statements/generate', methods=['POST'])
def generate_statement():
    data = request.get_json(force=True)
    previous_balance_id = data['previous_balance_id']
    start_date = data['start_date']
    end_date = data['end_date']

    date_range = (str(start_date) + '_' + str(end_date)).replace('-', '_')
    table = ge.create_statement_table(date_range)
    table_obj = table.__table__
    statement_summary_table = ga.create_statement_summary_table(date_range)
    statement_index = ge.add_statement_to_index(table, statement_summary_table)
    
    statement_balance_table = ge.create_statement_balance_table(table.__table__)
    ge.add_statement_balance_to_index(statement_index.id, statement_balance_table)
    
    if previous_balance_id == 'opening_balance':
        ge.add_opening_balance_to_index(id)
    else:
        ge.add_previous_balance_id_to_index(statement_index.id, previous_balance_id)

    artist_catalog_percentage = ge.find_track_percentage()
    artist_total = ge.find_artist_total(start_date, end_date, artist_catalog_percentage)
    ge.insert_into_table(artist_total, table_obj)
    expense_total = ge.find_expense_total(start_date, end_date, artist_catalog_percentage)
    ge.insert_expense_into_total(expense_total, table_obj)

    return json.dumps({'success': 'True', 'statement_index': statement_index.id})

@statements.route('/statements/<id>/generate-summary', methods=['POST'])
def generate_statement_summary(id):
    statement_summary_table = ga.lookup_statement_summary_table(id)
    i = statement_summary_table.delete()
    db.session.execute(i)
    db.session.commit()

    statement_previous_balance_by_artist = ga.create_statement_previous_balance_by_artist_subquery(id)
    statement_sales_by_artist = ga.create_statement_sales_by_artist_subquery(id)
    statement_advances_by_artist = ga.create_statement_advances_by_artist_subquery(id)
    statement_recoupables_by_artist = ga.create_statement_recoupables_by_artist_subquery(id)
    statement_by_artist = ga.create_statement_by_artist_subquery(
                                                        statement_previous_balance_by_artist,
                                                        statement_sales_by_artist,
                                                        statement_advances_by_artist,
                                                        statement_recoupables_by_artist,
                                                        )
    ga.insert_into_statement_summary(statement_by_artist, statement_summary_table)
    ga.insert_into_balance_table(id)
    return json.dumps({'success': 'true', 'index': id})


@statements.route('/statements/view', methods=['GET'])
def get_generated_statements():
    query = db.session.query(
            StatementGenerated.id,
            StatementGenerated.statement_detail_table,
            StatementGenerated.statement_summary_table).all()
    statement_generated_schema = StatementGeneratedSchema(many=True)
    statements = statement_generated_schema.dumps(query)
    return statements

@statements.route('/statements/<id>', methods=['GET'])
def get_statement_summary(id):
    """lookup statement summary table in index table with statement summary id"""
    statement_summary_table = ga.lookup_statement_summary_table(id)

    statement_detail_table = db.session.query(StatementGenerated).filter(StatementGenerated.id == id).first().statement_detail_table

    previous_balance_id = db.session.query(StatementGenerated).filter(StatementGenerated.id == id).first().previous_balance_id

    statement_for_all_artists = (
        db.session.query(statement_summary_table.c.artist_id,
                         statement_summary_table.c.previous_balance,
                         statement_summary_table.c.sales,
                         statement_summary_table.c.recoupables,
                         statement_summary_table.c.advances,
                         (statement_summary_table.c.sales - statement_summary_table.c.recoupables).label('total_to_split'),
                         cast(
                             ((statement_summary_table.c.sales - statement_summary_table.c.recoupables)/2),
                             Numeric(8, 2))
                         .label('split'),
                         cast(
                             ((statement_summary_table.c.sales - statement_summary_table.c.recoupables)/2 - statement_summary_table.c.advances + statement_summary_table.c.previous_balance),
                             Numeric(8, 2))
                         .label('balance_forward')
                         )
    ).subquery()

    statement_total = (db.session.query(
            func.coalesce(
                func.sum(statement_for_all_artists.c.balance_forward), 0
                )
            .label('total'))
    # .filter(statement_for_all_artists.c.balance_forward > 50)
    .first())

    statement_for_artist = (
        db.session.query(Artist, statement_for_all_artists)
            .join(Artist, Artist.id == statement_for_all_artists.c.artist_id)
            .all()
    ) 
    
    summary = {
            'statement_total': statement_total.total,
            'previous_balance': previous_balance_id,
            'statement': statement_detail_table,
            }

    detail = []
    
    for row in statement_for_artist:
        obj = {
                'id': row.Artist.id, 
                'artist_name': row.Artist.artist_name,
                'total_previous_balance': row.previous_balance,
                'total_sales': row.sales,
                'total_recoupable': row.recoupables,
                'total_advance': row.advances,
                'total_to_split': row.total_to_split,
                'split': row.split,
                'balance_forward': row.balance_forward,
                }
        detail.append(obj)

    json_res = {
            'summary': summary,
            'detail': detail,
            }

    return jsonify(json_res)

@statements.route('/statements/<id>/artist/<artist_id>', methods=['GET'])
def statement_detail_artist(id, artist_id):
    statement_summary_table = ga.lookup_statement_summary_table(id)

    statement_for_artist = (
        db.session.query(statement_summary_table.c.artist_id,
                         statement_summary_table.c.previous_balance,
                         statement_summary_table.c.sales,
                         statement_summary_table.c.recoupables,
                         statement_summary_table.c.advances,
                         (statement_summary_table.c.sales - statement_summary_table.c.recoupables).label('total_to_split'),
                         cast(
                             ((statement_summary_table.c.sales - statement_summary_table.c.recoupables)/2),
                             Numeric(8, 2))
                         .label('split'),
                         cast(
                             ((statement_summary_table.c.sales - statement_summary_table.c.recoupables)/2 - statement_summary_table.c.advances + statement_summary_table.c.previous_balance),
                             Numeric(8, 2))
                         .label('balance_forward')
                         )
    ).filter(statement_summary_table.c.artist_id == artist_id)

    summary = []
    
    for row in statement_for_artist:
        obj = {
                'previous_balance': row.previous_balance,
                'sales': row.sales,
                'recoupables': row.recoupables,
                'advances': row.advances,
                'total_to_split': row.total_to_split,
                'split': row.split,
                'balance_forward': row.balance_forward,
                }
        summary.append(obj)

    table = ga.get_statement_table(id)

    artist_name = db.session.query(Artist).filter(Artist.id == artist_id).first().artist_name

    statement_detail_table = db.session.query(StatementGenerated).filter(StatementGenerated.id == id).first().statement_detail_table
    
    income_summary = va.get_income_summary(table, artist_id)
    income = []
    for row in income_summary:
        obj = {
                'catalog_name': row.catalog_name,
                'combined_net': row.combined_net,
                'physical_net': row.physical_net,
                'digital_net': row.digital_net,
                }
        income.append(obj)

    expense_detail = va.get_expense_detail(table, artist_id)
    expense = []
    for row in expense_detail:
        obj = {
                'date': row.date.strftime("%Y-%m-%d"),
                'item': row.item_type,
                'vendor': row.customer,
                'detail': row.description,
                'expense': row.artist_net,
                }
        expense.append(obj)

    advance_detail = va.get_advance_detail(table, artist_id)
    advance = []
    for row in advance_detail:
        obj = {
                'date': row.date.strftime("%Y-%m-%d"),
                'item': row.item_type,
                'vendor': row.customer,
                'detail': row.description,
                'expense': row.artist_net,
                }
        advance.append(obj)
    json_res = {
            'income': income,
            'expense': expense,
            'advance': advance,
            }

    album_sales_detail = va.get_album_sales_detail(table, artist_id)
    album_sales = []
    for row in album_sales_detail:
        obj = {
                'catalog_name': row.catalog_name,
                'version_number': row.version_number,
                'format': row.format,
                'quantity': row.quantity,
                'net': row.net,
                }
        album_sales.append(obj)

    track_sales_detail = va.get_track_sales_detail(table, artist_id)
    
    track_sales = []

    for row in track_sales_detail:
        obj = {
                'track_name': row.track_name,
                'quantity': row.quantity,
                'net': row.net,
                }
        track_sales.append(obj)

    json_res = {
            'artist': artist_name,
            'statement': statement_detail_table,
            'summary': summary,
            'income': income,
            'expense': expense,
            'advance': advance,
            'album_sales': album_sales,
            'track_sales': track_sales,
            }

    return jsonify(json_res)

@statements.route('/statements/<id>/versions', methods=['GET'])
def statement_versions(id):
    statement_detail_table = ga.get_statement_table(id)
    
    query = (
        db.session.query(Version.id.label('id'),
                         Version.version_number.label('version_number'),
                         Version.format.label('format'),
                         Catalog.catalog_name.label('catalog_name'))
            .join(statement_detail_table, Version.id == statement_detail_table.c.version_id)
            .join(Catalog, Version.catalog_id == Catalog.id)
            .group_by(Version.id, Version.version_number, Version.format, Catalog.catalog_name)
            .order_by(Version.version_number)
            .all()
        )

    versions = []

    for row in query:
        obj = {
                'id': row.id,
                'version_number': row.version_number,
                'format': row.format,
                'catalog_name': row.catalog_name,
                }
        versions.append(obj)

    json_res = ({'versions': versions})

    return jsonify(json_res)
    
@statements.route('/statements/<id>/versions/<version_id>', methods=['DELETE'])
def delete_statement_versions(id, version_id):
    statement_detail_table = ga.get_statement_table(id)
    i = statement_detail_table.delete().where(statement_detail_table.c.version_id == version_id)
    db.session.execute(i)
    db.session.commit()
    return jsonify({'success': 'true'})

@statements.route('/statements/previous', methods=['GET'])
def get_previous_balances():
    return jsonify({'success': 'true'})

@statements.route('/statements/<id>', methods=['PUT'])
def edit_statement(id):
    data = request.get_json(force=True)
    statement_generated_obj = db.session.query(StatementGenerated).get(id)
    statement_generated_obj.previous_balance_id = data['previous_balance_id']
    db.session.commit()
    return jsonify({'success': 'true'})

@statements.route('/statements/<id>', methods=['DELETE'])
def delete_statement(id):
    query = db.session.query(StatementGenerated).filter(StatementGenerated.id==id).one()
    table_list = []
    table_list.append(query.statement_summary_table)
    table_list.append(query.statement_detail_table)
    table_list.append(query.statement_balance_table)
    db.session.query(StatementGenerated).filter(StatementGenerated.id==id).delete()
    metadata = MetaData(db.engine)
    metadata.reflect()
    for table_name in table_list:
        table = metadata.tables.get(table_name)
        table.drop()
    db.session.commit()
    return jsonify({'success': 'true'})

@statements.route('/statements/import-opening-balance', methods=['POST'])
def import_opening_balance():
    file = request.files['CSV']
    # check_statement = (
    #     db.session.query(StatementBalanceGenerated)
    #         .filter(StatementBalanceGenerated.statement_balance_name == 'statement_balance_opening')
    #         .all())

    # if len(check_statement) == 0:
    """Create table."""
    statement_balance_table = ge.create_statement_balance_table('opening')
    db.session.commit()
    """Add to statement balance table"""
    statement_generated_entry = StatementGenerated(
            statement_balance_table='opening_balance'
    )
    db.session.add(statement_generated_entry)
    db.session.commit()

    metadata = MetaData(db.engine)
    metadata.reflect()
    opening_balance_table = metadata.tables.get('opening_balance')
    # """Clear current values."""
    # db_session.execute("""DELETE FROM statement_balance_opening""")
    # db_session.commit()
    """Add new values from CSV."""
    df = pd.read_csv(file)
    df.to_sql('opening_balance', con=db.engine, if_exists='append', index=False)

    update = (
        opening_balance_table
            .update()
            .where(opening_balance_table.c.artist_name == Artist.artist_name)
            .values(artist_id=Artist.id)
    )
    db.session.execute(update)
    db.session.commit()
    # sel = (
    #     db.session.query(opening_balance_table, Artist.artist_name)
    #         .outerjoin(Artist, Artist.artist_name == opening_balance_table.c.artist_name).all()
    # )
    errors = (
        db.session.query(opening_balance_table)
            .outerjoin(Artist, Artist.artist_name == opening_balance_table.c.artist_name)
            .filter(Artist.artist_name == None).all()
    )
    if len(errors) > 0:
        return jsonify({'errors': len(errors)})
    return jsonify({'success': 'true'})
