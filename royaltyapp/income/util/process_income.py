from sqlalchemy import exc, func, cast

from royaltyapp.models import db, IncomePending, ImportedStatement, OrderSettings

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


def normalize_statement_id():
    db.session.execute("""
    UPDATE income_pending
    SET statement_id = imported_statement.id
    FROM imported_statement
    WHERE income_pending.statement = imported_statement.statement_name;
    """)
    db.session.commit()
    return True

def calculate_adjusted_amount():
    sel = (
    db.session.query(IncomePending.order_id.label('order_id'),
    IncomePending.amount.label('amount'),
    func.coalesce(OrderSettings.order_percentage, 0).label('order_percentage'),
    func.coalesce(OrderSettings.order_fee, 0).label('order_fee'))
    .filter(IncomePending.medium == 'physical')
    .outerjoin(OrderSettings, OrderSettings.distributor_id == IncomePending.distributor_id)
    .subquery()
    )

    sel = (
    db.session.query(sel.c.order_id,
    ((func.sum(sel.c.amount) * sel.c.order_percentage + sel.c.order_fee)
    / func.count(sel.c.order_id)).label('label_fee'))
    .distinct(sel.c.order_id)
    .group_by(sel.c.order_id,
    sel.c.order_percentage,
    sel.c.order_fee)
    .subquery()
    )

    """Upsert."""
    update = (
    IncomePending.__table__
    .update()
    .where(IncomePending.order_id == sel.c.order_id)
    .values(label_fee=sel.c.label_fee)
    )
    db.session.execute(update)
    """ZERO OUT FEE WHERE DOES NOT APPLY. This should be addressed not as a deletion, but a filter on insert."""
    update = (
    IncomePending.__table__
    .update()
    .where(IncomePending.medium == 'digital')
    .values(label_fee=0)
    )
    db.session.execute(update)
    update = (
    IncomePending.__table__
    .update()
    .where(IncomePending.amount < 5)
    .values(label_fee=0)
    )
    db.session.execute(update)
    update = (
    IncomePending.__table__
    .update()
    .values(label_net=(IncomePending.amount - IncomePending.label_fee))
    )
    db.session.execute(update)
    db.session.commit()
    return True
