from sqlalchemy import select
import pandas

from royaltyapp.models import PendingCatalog, PendingTrack, Artist, db, PendingVersion, Catalog, Version

def clean_catalog_df(df):
    df['catalog_artist'] = df['catalog_artist'].str.replace("’", "'")
    df['catalog_artist'] = df['catalog_artist'].str.title()
    return df

def clean_track_df(df):
    df['track_artist'] = df['track_artist'].str.replace("’", "'")
    df['track_artist'] = df['track_artist'].str.title()
    return df

def pending_catalog_to_artist(db):
    """Insert track artists to artists table."""
    sel = select([PendingCatalog.catalog_artist]).distinct()
    ins = Artist.__table__.insert().from_select(['artist_name'], sel)
    db.session.execute(ins)
    """Insert album artists into artists table"""
    db.session.execute("""INSERT INTO artist (artist_name) SELECT DISTINCT catalog_artist FROM pending_catalog
    LEFT JOIN artist ON pending_catalog.catalog_artist = artist.artist_name
    WHERE artist.artist_name IS NULL;""")
    db.session.commit()
    return True

def pending_catalog_to_catalog(db):
    """Import catalog into catalog table."""
    db.session.execute("""
    INSERT INTO catalog (catalog_number, catalog_name, artist_id)
    SELECT DISTINCT(pending_catalog.catalog_number), pending_catalog.catalog_name, artist.id
    FROM artist JOIN pending_catalog
    ON pending_catalog.catalog_artist = artist_name
    """)
    db.session.commit()
    return True

def pending_track_to_artist(db):
    """Insert track artists to artists table."""
    sel1 = select([PendingTrack.track_artist])
    sel2 = select([Artist.artist_name])
    sel = sel1.except_(sel2)

    ins = Artist.__table__.insert().from_select(['artist_name'], sel)
    db.session.execute(ins)
    # """Insert album artists into artists table"""
    # db.session.execute("""
    # INSERT INTO artist (artist_name)
    # SELECT DISTINCT track_artist FROM pending_track
    # LEFT JOIN artist ON pending_track.track_artist = artist.artist_name
    # WHERE artist.artist_name IS NULL;""")
    db.session.commit()
    return True

def pending_track_to_catalog(db):
    db.session.execute("""
    INSERT INTO track (isrc, track_name, track_number, artist_id)
    SELECT DISTINCT(pending_track.isrc), pending_track.track_name, track_number, artist.id
    FROM pending_track LEFT JOIN artist ON pending_track.track_artist = artist.artist_name
    """)

    db.session.execute("""
    INSERT INTO track_catalog_table (track_id, catalog_id)
    SELECT DISTINCT(track.id), catalog.id
    FROM pending_track
    JOIN track ON pending_track.isrc = track.isrc
    JOIN catalog ON pending_track.catalog_number = catalog.catalog_number;
    """)
    db.session.commit()
    return True

def pending_version_to_version(db):
    """ Import from pending version table to versions. """
    sel = (db.session.query(PendingVersion.version_number,
            PendingVersion.version_name,
            PendingVersion.upc,
            PendingVersion.format,
            Catalog.id))
    sel = (sel.join(Catalog,
        Catalog.catalog_number==PendingVersion.catalog_number)
        .distinct(PendingVersion.version_number)
        )
    ins = Version.__table__.insert().from_select(['version_number',
        'version_name',
        'upc',
        'format',
        'catalog_id'], sel)
    db.session.execute(ins)
    db.session.commit()
