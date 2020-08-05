import pandas as pd
import numpy as np

from royaltyapp.models import db, ExpensePending, Artist, Catalog, ExpenseType
from sqlalchemy import cast, func



def expense_matching_errors():
    sel = db.session.query(ExpensePending)
    sel = sel.outerjoin(Artist, Artist.artist_name == ExpensePending.artist_name)
    sel = sel.filter(Artist.artist_name == None, ExpensePending.catalog_number == None)

    return sel
    # sel1 = db.session.query(ExpensePending)
    # sel1 = sel1.outerjoin(Catalog, Catalog.catalog_number == ExpensePending.catalog_number)
    # sel1 = sel1.filter(Catalog.catalog_number == None, ExpensePending.artist_name == None)

    # sel2 = db.session.query(ExpensePending)
    # sel2 = sel2.outerjoin(ExpenseType, ExpenseType.expense_type == func.lower(ExpensePending.expense_type))
    # sel2 = sel2.filter(ExpenseType.id == None)

    # total_errors = sel.union(sel1)
    # total_errors = total_errors.union(sel2).all()

    # return total_errors


def artist_matching_errors():

    sel = db.session.query(ExpensePending)
    sel = sel.outerjoin(Artist, Artist.artist_name == ExpensePending.artist_name)
    sel = sel.filter(Artist.artist_name == None, ExpensePending.catalog_number == None).all()
    return sel


def catalog_matching_errors():

    sel1 = db.session.query(ExpensePending)
    sel1 = sel1.outerjoin(Catalog, Catalog.catalog_number == ExpensePending.catalog_number)
    sel1 = sel1.filter(Catalog.catalog_number == None, ExpensePending.artist_name == None).all()
    return sel1


def expense_type_matching_errors():

    sel2 = db.session.query(ExpensePending)
    sel2 = sel2.outerjoin(ExpenseType, ExpenseType.expense_type == func.lower(ExpensePending.expense_type))
    sel2 = sel2.filter(ExpenseType.id == None)
    return sel2

