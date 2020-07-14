from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
        VersionSchema, Track, TrackCatalogTable

import pandas as pd

from .helpers import clean_df

catalog = Blueprint('catalog', __name__)

@catalog.route('/catalog', methods=['GET'])
def all_catalog():
    result = Catalog.query.all()
    catalog_schema = CatalogSchema()
    catalogs_schema = CatalogSchema(many=True)
    return catalogs_schema.dumps(result)

@catalog.route('/catalog', methods=['POST'])
def add_catalog():
    data = request.get_json(force=True)
    try:
        new_catalog = Catalog(
                        catalog_number=data['catalog_number'],
                        catalog_name=data['catalog_name'],
                        artist_id=data['artist_id'],
                        )
        db.session.add(new_catalog)
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@catalog.route('/catalog/<id>', methods=['GET'])
def get_catalog(id):
    result = db.session.query(Catalog).filter(Catalog.id==id).one()
    catalog_schema = CatalogSchema()
    return catalog_schema.dumps(result)

@catalog.route('/catalog/<id>', methods=['DELETE'])
def delete_catalog(id):
    db.session.query(Catalog).filter(Catalog.id==id).delete()
    return jsonify({'success': 'true'})

@catalog.route('/version', methods=['POST'])
def add_version():
    data = request.get_json(force=True)
    catalog_id = data['catalog']
    try:
        for version in data['version']:
            new_version = Version(
                            version_number=version['version_number'],
                            version_name=version['version_name'],
                            upc=version['upc'],
                            format=version['format'],
                            catalog_id=catalog_id
                            )
            db.session.add(new_version)
            db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@catalog.route('/version', methods=['PUT'])
def edit_version():
    data = request.get_json(force=True)
    catalog_id = data['catalog']
    try:
        for version in data['version']:
            id = version['id']
            new_version = db.session.query(Version).get(id)
            new_version.upc = version['upc']
            new_version.version_number = version['version_number']
            new_version.version_name = version['version_name']
            new_version.format = version['format']
            db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@catalog.route('/version/<id>', methods=['GET'])
def get_version(id):
    result = db.session.query(Version).filter(Version.id==id).one()
    version_schema = VersionSchema()
    return version_schema.dumps(result)


@catalog.route('/catalog/<id>', methods=['PUT'])
def edit_catalog(id):
    data = request.get_json(force=True)
    obj = db.session.query(Catalog).get(id)

    if data['catalog_number']:
        obj.catalog_number = data['catalog_number']
    if data['catalog_name']:
        obj.catalog_name = data['catalog_name']
    if data['artist_id']:
        obj.surnom = data['artist_id']
    db.session.commit()
    return jsonify({'success': 'true'})

@catalog.route('/track', methods=['POST'])
def add_track():
    data = request.get_json(force=True)
    catalog_id = data['catalog']
    obj = db.session.query(Catalog).get(catalog_id)
    try:
        for track in data['track']:
            # add to track table
            new_track = Track(
                            track_number=track['track_number'],
                            track_name=track['track_name'],
                            isrc=track['isrc'],
                            artist_id=track['artist_id']
                            )
            obj.tracks.append(new_track)
            db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@catalog.route('/track', methods=['PUT'])
def edit_track():
    data = request.get_json(force=True)
    catalog_id = data['catalog']
    try:
        for track in data['tracks']:
            id = track['id']
            new_track = db.session.query(Track).get(id)
            new_track.track_number = track['track_number']
            new_track.track_name = track['track_name']
            new_track.track_name = track['track_name']
            db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@catalog.route('/catalog/import-catalog', methods=['POST'])
def import_catalog():
    data = request.get_json(force=True)
    df = pd.read_csv(data['body'])
    df = clean_df(df)
    df.to_sql('pending', con=engine, if_exists='append', index_label='id')
    return jsonify({'success': 'true'})


