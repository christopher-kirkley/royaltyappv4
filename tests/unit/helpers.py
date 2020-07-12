from royaltyapp.models import Artist, Catalog, Version, Track

def add_one_artist(db):
    new_artist = Artist(artist_name='Amanar',
                        prenom='Ahmed',
                        surnom='Ag Kaedi',
                        )
    db.session.add(new_artist)
    db.session.commit()

def add_one_catalog(db):
    add_one_artist(db)
    new_catalog = Catalog(catalog_number='SS-001',
                        catalog_name='Ishilan N-Tenere',
                        artist_id='1',
                        )
    db.session.add(new_catalog)
    db.session.commit()

def add_one_version(db):
    add_one_catalog(db)
    new_version = Version(
                        upc='123456',
                        version_number='SS-001lp',
                        version_name='Limited Vinyl',
                        format='LP',
                        catalog_id=1
                        )
    db.session.add(new_version)
    db.session.commit()

def add_one_track(db):
    add_one_catalog(db)
    obj = db.session.query(Catalog).first()
    new_track = Track(
                    track_number='123456',
                    track_name='SS-001lp',
                    isrc='Limited Vinyl',
                    )
    obj.track_catalog.append(new_track)
    db.session.commit()


