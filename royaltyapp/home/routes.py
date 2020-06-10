from flask import Blueprint, jsonify
from royaltyapp.models import Artist

home = Blueprint('home', __name__)

@home.route('/')
def index():
    result = Artist.query.all()
    return jsonify(result)
