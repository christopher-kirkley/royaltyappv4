from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

import os

from royaltyapp.models import Artist

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
    yield browser
    db.session.rollback()
    browser.quit()

def test_statement_generate(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'
    
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



    # """ User navigates to artist statement detail. """
    # browser.find_element_by_id('1').click()
    # assert browser.find_element_by_id('header').text == 'Statement Detail'
    # time.sleep(1)
    # table = browser.find_element_by_id('artist-statement-income')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('catalog_name').text == 'Akaline Kidal'
    # assert rows[1].find_element_by_id('digital_net').text == '0'
    # assert rows[1].find_element_by_id('physical_net').text == '30.45'
    # assert rows[1].find_element_by_id('combined_net').text == '30.45'

    # table = browser.find_element_by_id('artist-statement-expense')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('date').text == '2020-01-01'

    # table = browser.find_element_by_id('artist-statement-advance')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('date').text == '2020-01-01'

    # table = browser.find_element_by_id('album-sales')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('catalog_name').text == 'Akaline Kidal'

    # table = browser.find_element_by_id('track-sales')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('track_name').text == 'Adounia'

    # table = browser.find_element_by_id('artist-statement-summary')

    # """ User goes to edit statement. """
    # browser.find_element_by_id('statements_view').click()
    # browser.find_element_by_id('edit').click()
    # assert browser.find_element_by_id('header').text == 'Edit Statement'

    # time.sleep(2)
    # table = browser.find_element_by_id('edit-statement')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('version_number').text == 'SS-050cass'
    
    # rows[1].find_element_by_id('1').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('edit-statement')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('version_number').text == 'SS-050digi'

    # browser.find_element_by_id('update').click()

    # """ User returns to statement and sees it has been updated. """
    
def test_opening_balance(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'
    
    build_catalog(browser, test_client, db)

    browser.find_element_by_id('settings').click()

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


    
def test_opening_balance_errors(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'
    
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
    assert len(rows) == 2

    browser.find_element_by_id('update-2').click()

    time.sleep(1)

    table = browser.find_element_by_id('opening-balance-errors')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1


def test_statement_with_data(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'

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
    
    assert browser.find_element_by_id('summary-sales').text == "5.9"
    
    """ User exports statement."""

