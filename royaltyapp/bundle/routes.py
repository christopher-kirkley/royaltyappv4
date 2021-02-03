from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Catalog, CatalogSchema, Version, Bundle,\
        VersionSchema, Track, TrackCatalogTable, TrackSchema

import pandas as pd

from .helpers import clean_catalog_df, clean_track_df, pending_catalog_to_artist, pending_catalog_to_catalog, pending_version_to_version, pending_track_to_artist, pending_track_to_catalog

from royaltyapp.cache import cache


bundle = Blueprint('bundle', __name__)

@bundle.route('/bundle', methods=['GET'])
#@cache.cached(timeout=30)
def all_bundle():
    result = Catalog.query.all()
    bundle_schema = CatalogSchema()
    bundles_schema = CatalogSchema(many=True)
    return bundles_schema.dumps(result)

@bundle.route('/bundle', methods=['POST'])
def add_bundle():
    data = request.get_json(force=True)
    try:
        new_bundle = Bundle(
                        bundle_number=data['bundle_number'],
                        bundle_name=data['bundle_name'],
                        )
        db.session.add(new_bundle)
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true',
                    'id': new_bundle.id })

@bundle.route('/catalog/<id>', methods=['GET'])
def get_bundle(id):
    result = db.session.query(Catalog).filter(Catalog.id==id).one()
    bundle_schema = CatalogSchema()
    return bundle_schema.dumps(result)

@bundle.route('/catalog/<id>', methods=['DELETE'])
def delete_bundle(id):
    db.session.query(Catalog).filter(Catalog.id==id).delete()
    db.session.commit()
    return jsonify({'success': 'true'})

@bundle.route('/version', methods=['POST'])
def add_version():
    data = request.get_json(force=True)
    bundle_id = data['catalog']
    try:
        for version in data['version']:
            new_version = Version(
                            version_number=version['version_number'],
                            version_name=version['version_name'],
                            upc=version['upc'],
                            format=version['format'],
                            bundle_id=catalog_id
                            )
            db.session.add(new_version)
            db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

