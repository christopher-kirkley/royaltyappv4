from sqlalchemy import exc

from royaltyapp.models import db, IncomePending, ImportedStatement

def normalize_distributor():
    db.session.execute("""
    UPDATE income_pending
    SET distributor_id = income_distributor.id
    FROM income_distributor
    WHERE income_pending.distributor = income_distributor.distributor_name;
    """)
    db.session.commit()

def normalize_version():
    db.session.execute("""
    UPDATE income_pending
    set version_id = version.id
    FROM version
    WHERE income_pending.upc_id = version.upc;
    """)
    db.session.commit()

def normalize_track():
    db.session.execute("""
    UPDATE income_pending
    SET track_id = track.id
    FROM track
    WHERE income_pending.isrc_id = track.isrc;
    """)
    db.session.commit()

def insert_into_imported_statements():
    submitted_statements = (db.session.query(IncomePending.statement,
    IncomePending.distributor_id,)
    .distinct().all()
    )
    for item in submitted_statements:
        try:
            i = (ImportedStatement.__table__
            .insert().values(statement_name=item.statement,
            transaction_type='income',
            income_distributor_id=item.distributor_id)
            )
            db.session.execute(i)
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return f"Failed on {item.statement}, already in total sales."
    return True
