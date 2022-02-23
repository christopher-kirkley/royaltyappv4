from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

import os

from royaltyapp.models import Artist, add_admin_user

from helpers import login

base = os.path.basename(__file__)
CASE = base.split('.')[0]

def build_catalog(browser, test_client, db):
    """ User uploads catalog and versions. """
    browser.find_element_by_id('catalog').click()
    time.sleep(1)
    browser.find_element_by_id('import_catalog').click()
    path = os.getcwd() + f"/tests/func/{CASE}/catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('catalog_upload').click()

    path = os.getcwd() + f"/tests/func/{CASE}/version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('version_upload').click()

    path = os.getcwd() + f"/tests/func/{CASE}/track.csv"
    browser.find_element_by_id('track_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('track_upload').click()

    """ User uploads bundles. """
    browser.find_element_by_id('bundle').click()
    time.sleep(1)
    browser.find_element_by_id('import_bundle').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bundle.csv"
    browser.find_element_by_id('bundle_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('bundle_upload').click()

@pytest.fixture
def browser(db):
    browser = webdriver.Firefox()
    add_admin_user(db)
    yield browser
    db.session.rollback()
    browser.quit()

def test_statement_generate(browser, test_client, db):
    login(browser)
    time.sleep(3)
    
    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User navigates to first statement to view main statement."""
    browser.find_element_by_id('view-1').click()
    time.sleep(2)
    assert browser.find_element_by_id('header').text == 'Statement Summary'
    assert browser.find_element_by_id('statement-name').text == 'statement_2020_01_01_2020_01_31'
    assert browser.find_element_by_id('current-owed').text == 'Current Owed: $0'

    """ User goes to edit statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('edit-1').click()

    assert browser.find_element_by_id('header').text == 'Edit Statement'

    """ User deletes statement."""
    browser.find_element_by_id('delete-statement').click()
    time.sleep(1)

    """ User redirected to statement page, verfies statement is gone."""
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 0

def test_opening_balance(browser, test_client, db):
    login(browser)
    
    build_catalog(browser, test_client, db)

    browser.find_element_by_id('settings').click()
    
    path = os.getcwd() + f"/tests/func/{CASE}/opening_balance.csv"
    browser.find_element_by_id('opening-balance-to-upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('opening-balance-upload').click()

    time.sleep(2)
    
    assert browser.find_element_by_id('header').text == 'Statements'

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('opening_balance').click()
    browser.find_element_by_id('submit').click()
    time.sleep(2)

    """ User goes to view statement and confirms created. """

    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    browser.find_element_by_id('view-2').click()

    time.sleep(1)

    assert browser.find_element_by_id('current-owed').text == 'Current Owed: $150'
    assert browser.find_element_by_id('previous-balance').text == 'Previous Balance Table: opening_balance'

def test_opening_balance_errors(browser, test_client, db):
    login(browser)
    
    build_catalog(browser, test_client, db)
    
    browser.get('http://localhost:3000/artists')

    browser.find_element_by_id('settings').click()
    
    path = os.getcwd() + f"/tests/func/{CASE}/opening_balance_errors.csv"
    browser.find_element_by_id('opening-balance-to-upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('opening-balance-upload').click()

    time.sleep(1)

    assert browser.find_element_by_id('header').text == 'Fix Opening Balance Errors'
    table = browser.find_element_by_id('opening-balance-errors')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 4

    time.sleep(1)
    
    browser.find_element_by_id('updatebutton-2').click()

    time.sleep(1)

    table = browser.find_element_by_id('opening-balance-errors')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3


def test_statement_with_data(browser, test_client, db):
    login(browser)

    build_catalog(browser, test_client, db)

    """ User goes to upload income. """
    browser.find_element_by_id('income').click()

    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'bandcamp.csv'
    
    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User navigates to first statement to view main statement."""
    browser.find_element_by_id('view-1').click()
    time.sleep(2)
    assert browser.find_element_by_id('header').text == 'Statement Summary'
    assert browser.find_element_by_id('statement-name').text == 'statement_2020_01_01_2020_01_31'
    time.sleep(1)

    """ User navigates to first artist on statement """
    browser.find_element_by_id('view-1').click()
    time.sleep(2)
    
    assert browser.find_element_by_id('summary-sales').text == "$5.9"
    
    """ User exports statement."""

def test_generate_statement_with_open_balance_and_sales(browser, test_client, db):
    
    login(browser)

    build_catalog(browser, test_client, db)

    """ Add opening balance. """
    browser.find_element_by_id('settings').click()
    
    path = os.getcwd() + f"/tests/func/{CASE}/opening_balance.csv"
    browser.find_element_by_id('opening-balance-to-upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('opening-balance-upload').click()

    """ User goes to upload income. """
    browser.find_element_by_id('income').click()

    time.sleep(1)
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()
    time.sleep(1)

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('opening_balance').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User navigates to first statement to view main statement."""
    browser.find_element_by_id('view-2').click()
    time.sleep(2)
    assert browser.find_element_by_id('header').text == 'Statement Summary'
    assert browser.find_element_by_id('statement-name').text == 'statement_2020_01_01_2020_01_31'

def test_generate_statement_with_open_balance_errors_and_sales(browser, test_client, db):
    
    login(browser)

    build_catalog(browser, test_client, db)

    browser.get('http://localhost:3000/artists')


    """ User goes to upload income. """
    browser.find_element_by_id('income').click()

    time.sleep(1)
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()
    time.sleep(1)

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User goes to delete statement. """
    browser.find_element_by_id('edit-1').click()
    time.sleep(1)
    browser.find_element_by_id('delete-statement').click()

    time.sleep(5)

    """ Add opening balance. """
    browser.find_element_by_id('settings').click()
    
    path = os.getcwd() + f"/tests/func/{CASE}/opening_balance_errors.csv"
    browser.find_element_by_id('opening-balance-to-upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('opening-balance-upload').click()

    time.sleep(1)

    assert browser.find_element_by_id('header').text == 'Fix Opening Balance Errors'
    table = browser.find_element_by_id('opening-balance-errors')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 4

    browser.find_element_by_id('updatebutton-2').click()
    browser.find_element_by_id('updatebutton-3').click()
    browser.find_element_by_id('updatebutton-4').click()

    time.sleep(1)

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('opening_balance').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

def test_delete_version_in_statement(browser, test_client, db):
    
    login(browser)

    build_catalog(browser, test_client, db)

    browser.get('http://localhost:3000/artists')

    """ User goes to upload income. """
    browser.find_element_by_id('income').click()

    time.sleep(1)
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp-2.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()
    time.sleep(1)

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    browser.find_element_by_id('edit-1').click()

    time.sleep(1)

    table = browser.find_element_by_id('edit-versions')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    browser.find_element_by_id('1').click()

    table = browser.find_element_by_id('edit-versions')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 2

    """ User goes to view statement, sees it is unchanged. """
    browser.find_element_by_id('statements').click()
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    browser.find_element_by_id('edit-1').click()

    time.sleep(1)

    table = browser.find_element_by_id('edit-versions')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    browser.find_element_by_id('1').click()

    browser.find_element_by_id('save').click()

    time.sleep(1)

    assert browser.find_element_by_id('header').text == 'Statements'

    browser.find_element_by_id('edit-1').click()

    time.sleep(1)

    table = browser.find_element_by_id('edit-versions')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 2

def test_can_generate_expense_with_no_version(browser, test_client, db):
    login(browser)

    """ User uploads catalog and versions. """
    browser.find_element_by_id('catalog').click()
    time.sleep(1)
    browser.find_element_by_id('import_catalog').click()
    path = os.getcwd() + f"/tests/func/{CASE}/catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('catalog_upload').click()

    """ User goes to expense. """
    browser.find_element_by_id('expense').click()

    """ User goes to upload expense. """
    browser.find_element_by_id('import_expense').click()

    """ User uploads a expense file."""
    path = os.getcwd() + f"/tests/func/{CASE}/expense_catalog.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('catalog_source').click()
    browser.find_element_by_id('upload_statement').click()

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_catalog.csv'

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()
    time.sleep(1)

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('07012019')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('12312019')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User navigates to first statement to view main statement."""
    browser.find_element_by_id('view-1').click()
    time.sleep(2)
    assert browser.find_element_by_id('header').text == 'Statement Summary'
    assert browser.find_element_by_id('statement-name').text == 'statement_2019_07_01_2019_12_31'

    """ User navigates to first artist on statement """
    browser.find_element_by_id('view-1').click()
    time.sleep(2)
    
    assert browser.find_element_by_id('summary-sales').text == "$5.9"
    
    """ User exports statement."""

    time.sleep(1000)


