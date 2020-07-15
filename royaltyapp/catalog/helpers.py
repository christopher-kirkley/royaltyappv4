from sqlalchemy import select
import pandas

from royaltyapp.models import Pending, Artist, db, PendingVersion, Catalog, Version

def clean_df(df):
    df['track_artist'] = df['track_artist'].str.replace("’", "'")
    df['track_artist'] = df['track_artist'].str.title()
    df['catalog_artist'] = df['catalog_artist'].str.replace("’", "'")
    df['catalog_artist'] = df['catalog_artist'].str.title()
    return df

def pending_to_artist(db):
    """Insert track artists to artists table."""
    sel = select([Pending.track_artist]).distinct()
    ins = Artist.__table__.insert().from_select(['artist_name'], sel)
    db.session.execute(ins)
    """Insert album artists into artists table"""
    db.session.execute("""INSERT INTO artist (artist_name) SELECT DISTINCT catalog_artist FROM pending
    LEFT JOIN artist ON pending.catalog_artist = artist.artist_name
    WHERE artist.artist_name IS NULL;""")
    db.session.commit()
    return True

def pending_to_catalog(db):
    """Import catalog into catalog table."""
    db.session.execute("""
    INSERT INTO catalog (catalog_number, catalog_name, artist_id)
    SELECT DISTINCT(pending.catalog_number), pending.catalog_name, artist.id
    FROM artist JOIN pending
    ON pending.catalog_artist = artist_name
    """)

    db.session.execute("""
    INSERT INTO track (isrc, track_name, track_number, artist_id)
    SELECT DISTINCT(pending.isrc), pending.track_name, track_number, artist.id
    FROM artist JOIN pending
    ON pending.track_artist = artist_name;
    """)

    db.session.execute("""
    INSERT INTO track_catalog_table (track_id, catalog_id)
    SELECT DISTINCT(track.id), catalog.id
    FROM pending
    JOIN track ON pending.isrc = track.isrc
    JOIN catalog ON pending.catalog_number = catalog.catalog_number;
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
