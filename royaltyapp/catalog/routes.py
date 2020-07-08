from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Catalog, CatalogSchema, Version,\
        VersionSchema

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
            if 'id' in version:
                """Update if posting version id"""
                id = version['id']
                new_version = db.session.query(Version).get(id)
                new_version.upc = version['upc']
                new_version.version_number = version['version_number']
                new_version.version_name = version['version_name']
                new_version.format = version['format']
            else:
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

# @artists.route('/artists', methods=['POST'])
# def add_artist():
#     data = request.get_json(force=True)
#     try:
#         new_artist = Artist(
#                         artist_name=data['artist_name'],
#                         prenom=data['prenom'],
#                         surnom=data['surnom'],
#                         )
#         db.session.add(new_artist)
#         db.session.commit()
#     except exc.DataError:
#         db.session.rollback()
#         return jsonify({'success': 'false'})
#     return jsonify({'success': 'true'})


# @artists.route('/temp', methods=['GET', 'POST'])
# def temp():
#     new_artist = Artist(
#                     artist_name=235423,
#                     prenom='chaewraew',
#                     surnom='aerewr'
#                     )
#     db.session.add(new_artist)
#     db.session.commit()

#     return 'yaya'
