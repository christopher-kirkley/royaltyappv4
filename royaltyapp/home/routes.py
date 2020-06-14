from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from royaltyapp.models import Artist, db

home = Blueprint('home', __name__,
                template_folder='templates')

@home.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('home.new'))
    
    return render_template('home/index.html')

@home.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        artist_name = request.form.get('artist_name')
        prenom = request.form.get('prenom')
        surnom = request.form.get('surnom')
        new_artist = Artist(artist_name = artist_name,
                            prenom = prenom,
                            surnom = surnom,
                            )
        db.session.add(new_artist)
        db.session.commit()
        return redirect(url_for('home.index'))
    
    return render_template('home/new.html')
