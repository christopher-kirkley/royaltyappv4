from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Artist, ArtistSchema, Catalog, CatalogSchema, Track, TrackSchema, Contact
import json

artists = Blueprint('artists', __name__)

@artists.route('/artists', methods=['GET'])
def all_artists():
    result = Artist.query.all()
    artist_schema = ArtistSchema()
    artists_schema = ArtistSchema(many=True)
    return artists_schema.dumps(result)

@artists.route('/artists/<id>', methods=['GET'])
def one_artist(id):
    result = db.session.query(Artist).filter(Artist.id==id).one()
    artist_schema = ArtistSchema()
    return artist_schema.dumps(result)

@artists.route('/artists/<id>', methods=['PUT'])
def edit_artist(id):
    data = request.get_json(force=True)
    obj = db.session.query(Artist).get(id)

    if data['artist_name']:
        obj.artist_name = data['artist_name']
    if data['prenom']:
        obj.prenom = data['prenom']
    if data['surnom']:
        obj.surnom = data['surnom']

    db.session.commit()
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
    return jsonify({'success': 'true',
                    'id': new_artist.id })

@artists.route('/artists/<id>', methods=['DELETE'])
def delete_artist(id):
    db.session.query(Artist).filter(Artist.id==id).delete()
    db.session.commit()
    return jsonify({'success': 'true'})

@artists.route('/artists/<id>/catalog', methods=['GET'])
def get_catalog_by_artist(id):
    result = db.session.query(Catalog).filter(Catalog.artist_id==id).all()
    catalog_schema = CatalogSchema(many=True)
    return catalog_schema.dumps(result)

@artists.route('/artists/<id>/track', methods=['GET'])
def get_tracks_by_artist(id):
    result = db.session.query(Track).filter(Track.artist_id==id).all()
    track_schema = TrackSchema(many=True)
    return track_schema.dumps(result)

@artists.route('/contacts', methods=['POST'])
def add_contact():
    data = request.get_json(force=True)
    try:
        new_contact = Contact(
                        prenom=data['contact_prenom'],
                        middle=data['contact_middle'],
                        surnom=data['contact_surnom'],
                        address=data['address'],
                        phone=data['phone'],
                        bank_name=data['bank_name'],
                        bban=data['bban'],
                        notes=data['notes'],
                        artist_id=data['artist_id'],
                        )
        db.session.add(new_contact)
        db.session.commit()
    except exc.DataError:
        db.session.rollback()
        return jsonify({'success': 'false'})
    return jsonify({'success': 'true'})

@artists.route('/contacts/<id>', methods=['PUT'])
def edit_contact(id):
    data = request.get_json(force=True)
    obj = db.session.query(Contact).get(id)

    if data['contact_prenom']:
        obj.prenom = data['contact_prenom']
    if data['contact_middle']:
        obj.middle = data['contact_middle']
    if data['contact_surnom']:
        obj.surnom = data['contact_surnom']
    if data['address']:
        obj.address = data['address']
    if data['phone']:
        obj.phone = data['phone']
    if data['bank_name']:
        obj.bank_name = data['bank_name']
    if data['bban']:
        obj.bban = data['bban']
    if data['notes']:
        obj.notes = data['notes']

    db.session.commit()
    return jsonify({'success': 'true'})
