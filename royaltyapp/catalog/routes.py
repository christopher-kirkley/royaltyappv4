from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Catalog


catalog = Blueprint('catalog', __name__)

@catalog.route('/catalog', methods=['GET'])
def all_catalog():
    result = Catalog.query.all()
    return jsonify(result)

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

# @artists.route('/artists', methods=['PUT'])
# def edit_artist():
#     data = request.get_json(force=True)
#     id_to_edit = data['id']
#     obj = db.session.query(Artist).get(id_to_edit)

#     if data['artist_name']:
#         obj.artist_name = data['artist_name']
#     if data['prenom']:
#         obj.prenom = data['prenom']
#     if data['surnom']:
#         obj.surnom = data['surnom']

#     return jsonify({'success': 'true'})

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

# @artists.route('/artists/delete/<id>', methods=['DELETE'])
# def delete_artist(id):
#     db.session.query(Artist).filter(Artist.id==id).delete()
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
