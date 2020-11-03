from sqlalchemy import exc, func, cast

from royaltyapp.models import db, ExpensePending, Artist, Catalog, ExpenseType, ImportedStatement, ExpenseTotal

def normalize_artist():
    update = (
        ExpensePending.__table__
        .update()
        .where(ExpensePending.artist_name == Artist.artist_name)
        .values(artist_id=Artist.id)
        )
    db.session.execute(update)
    db.session.commit()

def normalize_catalog():
    update = (
        ExpensePending.__table__
        .update()
        .where(ExpensePending.catalog_number == Catalog.catalog_number)
        .values(catalog_id=Catalog.id)
        )
    db.session.execute(update)
    db.session.commit()

def normalize_expense_type():
    update = (
        ExpensePending.__table__
        .update()
        .where(func.lower(ExpensePending.expense_type) == ExpenseType.expense_type)
        .values(expense_type_id=ExpenseType.id)
        )
    db.session.execute(update)
    db.session.commit()

def insert_into_imported_statements():
    submitted_statements = (
            db.session.query(
                ExpensePending.statement,
                func.min(ExpensePending.date).label('start_date'),
                func.max(ExpensePending.date).label('end_date'),
                )
            .group_by(ExpensePending.statement,)
            .distinct().all()
    )
    for item in submitted_statements:
        try:
            i = (
                    ImportedStatement.__table__
                    .insert().values(
                        statement_name=item.statement,
                        transaction_type='expense',
                        start_date=item.start_date,
                        end_date=item.end_date,
                        )
                    )
            db.session.execute(i)
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return f"Failed on {item.statement}, already in total sales."
    return True

def normalize_statement_id():
    update = (
    ExpensePending.__table__
    .update()
    .where(ExpensePending.statement == ImportedStatement.statement_name)
    .values(imported_statement_id=ImportedStatement.id)
    )
    db.session.execute(update)
    return True

def move_from_pending_expense_to_total():
    sel = db.session.query(ExpensePending.date,
    ExpensePending.vendor,
    ExpensePending.description,
    ExpensePending.net,
    ExpensePending.artist_id,
    ExpensePending.catalog_id,
    ExpensePending.imported_statement_id,
    ExpensePending.expense_type_id,
    ExpensePending.item_type,
    )

    ins = ExpenseTotal.__table__.insert().from_select(['date',
    'vendor',
    'description',
    'net',
    'artist_id',
    'catalog_id',
    'imported_statement_id',
    'expense_type_id',
    'item_type',
    ], sel)
    db.session.execute(ins)

    """Clean up pending table."""
    i = ExpensePending.__table__.delete()
    db.session.execute(i)

    db.session.commit()


# def calculate_adjusted_amount():
#     sel = (
#     db.session.query(IncomePending.order_id.label('order_id'),
#     IncomePending.amount.label('amount'),
#     func.coalesce(OrderSettings.order_percentage, 0).label('order_percentage'),
#     func.coalesce(OrderSettings.order_fee, 0).label('order_fee'))
#     .filter(IncomePending.medium == 'physical')
#     .outerjoin(OrderSettings, OrderSettings.distributor_id == IncomePending.distributor_id)
#     .subquery()
#     )

#     sel = (
#     db.session.query(sel.c.order_id,
#     ((func.sum(sel.c.amount) * sel.c.order_percentage + sel.c.order_fee)
#     / func.count(sel.c.order_id)).label('label_fee'))
#     .distinct(sel.c.order_id)
#     .group_by(sel.c.order_id,
#     sel.c.order_percentage,
#     sel.c.order_fee)
#     .subquery()
#     )

#     """Upsert."""
#     update = (
#     IncomePending.__table__
#     .update()
#     .where(IncomePending.order_id == sel.c.order_id)
#     .values(label_fee=sel.c.label_fee)
#     )
#     db.session.execute(update)
#     """ZERO OUT FEE WHERE DOES NOT APPLY. This should be addressed not as a deletion, but a filter on insert."""
#     update = (
#     IncomePending.__table__
#     .update()
#     .where(IncomePending.medium == 'digital')
#     .values(label_fee=0)
#     )
#     db.session.execute(update)
#     update = (
#     IncomePending.__table__
#     .update()
#     .where(IncomePending.amount < 5)
#     .values(label_fee=0)
#     )
#     db.session.execute(update)
#     update = (
#     IncomePending.__table__
#     .update()
#     .values(label_net=(IncomePending.amount - IncomePending.label_fee))
#     )
#     db.session.execute(update)
#     db.session.commit()
#     return True

# def move_from_pending_income_to_total():
#     sel = db.session.query(IncomePending.date,
#     IncomePending.quantity,
#     IncomePending.amount,
#     IncomePending.label_fee,
#     IncomePending.label_net,
#     IncomePending.track_id,
#     IncomePending.version_id,
#     IncomePending.medium,
#     IncomePending.type,
#     IncomePending.statement_id,
#     IncomePending.distributor_id,
#     IncomePending.customer,
#     IncomePending.city,
#     IncomePending.region,
#     IncomePending.country)

#     ins = IncomeTotal.__table__.insert().from_select(['date',
#     'quantity',
#     'amount',
#     'label_fee',
#     'label_net',
#     'track_id',
#     'version_id',
#     'medium',
#     'type',
#     'imported_statement_id',
#     'income_distributor_id',
#     'customer',
#     'city',
#     'region',
#     'country'],
#      sel)
#     db.session.execute(ins)
#     db.session.commit()

#     i = IncomePending.__table__.delete()
#     db.session.execute(i)
#     db.session.commit()
