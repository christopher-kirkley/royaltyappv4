from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Artist, ArtistSchema
import json

artists = Blueprint('artists', __name__)

@artists.route('/artists', methods=['GET'])
def all_artists():
    result = Artist.query.all()
    artist_schema = ArtistSchema()
    artists_schema = ArtistSchema(many=True)
    return artists_schema.dumps(result)

@artists.route('/artists', methods=['PUT'])
def edit_artist():
    data = request.get_json(force=True)
    id_to_edit = data['id']
    obj = db.session.query(Artist).get(id_to_edit)

    if data['artist_name']:
        obj.artist_name = data['artist_name']
    if data['prenom']:
        obj.prenom = data['prenom']
    if data['surnom']:
        obj.surnom = data['surnom']

    return jsonify({'success': 'true'})

@artists.route('/artists', methods=['POST'])
def add_artist():
    data = request.get_json(force=True)
    try:
        new_artist = Artist(
                        artist_name=data['artist_name'],
                        prenom=data['prenom'],
                        surnom=data['surnom'],
                        )
        db.session.add(new_artist)
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@artists.route('/artists/delete/<id>', methods=['DELETE'])
def delete_artist(id):
    db.session.query(Artist).filter(Artist.id==id).delete()
    return jsonify({'success': 'true'})

