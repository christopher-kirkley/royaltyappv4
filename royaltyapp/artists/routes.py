from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from royaltyapp.models import db, Artist


artists = Blueprint('artists', __name__)

@artists.route('/artists', methods=['GET'])
def all_artists():
    result = Artist.query.all()
    return jsonify(result)

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

@artists.route('/temp', methods=['GET', 'POST'])
def temp():
    new_artist = Artist(
                    artist_name=235423,
                    prenom='chaewraew',
                    surnom='aerewr'
                    )
    db.session.add(new_artist)
    db.session.commit()

    return 'yaya'
