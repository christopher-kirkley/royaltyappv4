from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Catalog, CatalogSchema, Version, Bundle, BundleVersionTable, VersionSchema, Track, TrackCatalogTable, TrackSchema, BundleSchema

import pandas as pd

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
    bundle_id = new_bundle.id
    obj = db.session.query(Bundle).get(bundle_id)
    for version in data['bundle_version']:
        try:
            version_obj = db.session.query(Version).get(version['version_id'])
            obj.version_bundle.append(version_obj)
            db.session.commit()
        except exc.DataError:
            db.session.rollback()
            return jsonify({'success': 'false'})
    return jsonify({'success': 'true',
                    'id': new_bundle.id })


@bundle.route('/bundle/<id>', methods=['GET'])
def get_bundle(id):
    result = db.session.query(Bundle).filter(Bundle.id==id).one()
    bundle_schema = BundleSchema()
    return bundle_schema.dumps(result)

@bundle.route('/bundle/<id>', methods=['DELETE'])
def delete_bundle(id):
    bundle = db.session.query(Bundle).filter(Bundle.id==1).first()
    db.session.delete(bundle)
    db.session.commit()
    return jsonify({'success': 'true'})

@bundle.route('/bundle', methods=['PUT'])
def edit_bundle_version():
    data = request.get_json(force=True)
    bundle_id=data['bundle_id']
    
    # edit bundle info  
    bundle_obj = db.session.query(Bundle).get(bundle_id)
    bundle_obj.bundle_number = data['bundle_number']
    bundle_obj.bundle_name = data['bundle_name']
    db.session.commit()

    # remove bundle versions
    bundle = db.session.query(Bundle).get(1)
    bundle.version_bundle = []
    db.session.commit()

    # add new bundle versions
    obj = db.session.query(Bundle).get(bundle_id)
    for version in data['bundle_version']:
        try:
            version_obj = db.session.query(Version).get(version['version_id'])
            obj.version_bundle.append(version_obj)
            db.session.commit()
        except exc.DataError:
            db.session.rollback()
            return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})
