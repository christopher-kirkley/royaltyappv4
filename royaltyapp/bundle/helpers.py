from sqlalchemy import select
import pandas

from royaltyapp.models import PendingCatalog, PendingTrack, Artist, db, PendingBundle, Catalog, Version

def pending_bundle_to_bundle(db):
    db.session.execute("""
    INSERT INTO bundle (bundle_number, bundle_name)
    SELECT DISTINCT(pending_bundle.bundle_number), pending_bundle.bundle_name
    FROM pending_bundle
    """)

    db.session.execute("""
    INSERT INTO bundle_version_table (bundle_id, version_id)
    SELECT DISTINCT(bundle.id), version.id
    FROM pending_bundle
    JOIN bundle ON pending_bundle.bundle_number = bundle.bundle_number
    JOIN version ON pending_bundle.version_number = version.version_number;
    """)
    db.session.commit()
    return True

