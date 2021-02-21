from sqlalchemy import exc, func, cast

from royaltyapp.models import db, IncomePending, ImportedStatement, OrderSettings, IncomeTotal, Bundle, BundleVersionTable


def add_missing_upc():
    """album"""

    # stmt = (
    #         update(IncomePending).
    #         where(IncomePending.__table__.c.version_number.
    #             replace(Column('version_number', '-', 'version_number'))== Version.__table__.c.version_number).
    #         # where(IncomePending.__table__.c.upc_id == '').
    #         values(upc_id = Version.upc)
    #         )
    # db.session.execute(stmt)
    # db.session.commit()

    """Version hyphens"""
    db.engine.execute("""
    UPDATE
    income_pending
    SET
    upc_id = version.upc
    FROM
    version
    WHERE
    LOWER(REPLACE(version.version_number, '-', '')) =
    LOWER(REPLACE(income_pending.version_number, '-', ''))
    OR
    (income_pending.upc_id is NULL AND income_pending.upc_id = '')
    """)

    db.engine.execute("""
    UPDATE
    income_pending
    SET
    upc_id = version.upc
    FROM
    version
    WHERE
    LOWER(version.version_number) = LOWER(income_pending.version_number)
    AND
    income_pending.upc_id is NULL
    """)

    """Update bundle upc"""
    db.engine.execute("""
    UPDATE
    income_pending
    SET
    upc_id = bundle.upc
    FROM
    bundle
    WHERE
    LOWER(REPLACE(bundle.bundle_number, '-', '')) = LOWER(REPLACE(income_pending.version_number, '-', ''))
    OR
    (income_pending.upc_id is NULL AND income_pending.upc_id = '')
    """)

    db.session.commit()

def match_upc_on_catalog_name():
    """Match on catalog name and medium"""

    db.engine.execute("""
    UPDATE
    income_pending
    SET
    upc_id = version.upc
    FROM
    version
    JOIN
    catalog
    ON version.catalog_id = Catalog.id
    WHERE
    version.format = income_pending.medium
    AND
    LOWER(catalog.catalog_name) = LOWER(income_pending.album_name)
    AND
    income_pending.type = 'album'
    AND
    income_pending.upc_id IS NULL
    """)

    db.session.commit()
    
def add_missing_version_number():
    """album"""
    db.engine.execute("""
    UPDATE
    income_pending
    SET
    version_number = version.version_number
    FROM
    version
    WHERE
    income_pending.upc_id = version.upc
    """)
    db.session.commit()


