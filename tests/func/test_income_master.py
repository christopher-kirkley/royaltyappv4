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

def test_import_master(browser, test_client, db):
    login(browser)

    build_catalog(browser, test_client, db)

    """ User goes to upload income. """
    browser.find_element_by_id('income').click()

    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/master.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('master').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'master.csv'
    
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
    
    assert browser.find_element_by_id('summary-sales').text == "$1500"
    

