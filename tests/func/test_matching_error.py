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

@pytest.fixture
def browser(db):
    browser = webdriver.Firefox()
    add_admin_user(db)
    yield browser
    db.session.rollback()
    browser.quit()

def test_returns(browser, test_client, db):
    login(browser)

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

    """ User goes to the bundle view """
    browser.find_element_by_id('bundle').click()

    assert browser.find_element_by_id('header').text == 'Bundle Items'

    """ User clicks to add a new catalog item """
    add_bundle = browser.find_element_by_id('add_bundle')
    add_bundle.click()

    """ User fills out bundle info. """
    bundle_number = browser.find_element_by_id('bundle_number')
    bundle_number.send_keys('SS-3MYS')
    bundle_name = browser.find_element_by_id('bundle_name')
    bundle_name.send_keys('Three Mystery Items')
    upc = browser.find_element_by_id('upc')
    upc.send_keys('999111')

    browser.find_element_by_id('add_version').click()
    browser.find_element_by_id('1').click()
    browser.find_element_by_id('add_version').click()
    browser.find_element_by_id('3').click()

    submit = browser.find_element_by_id('submit')
    submit.click()

    """ User goes to income. """
    browser.find_element_by_id('income').click()
    browser.find_element_by_id('income-data').text == 'No data'

    """ User goes to upload income. """
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('upc_matching_errors').text == "You have 5 UPC matching errors."
    browser.find_element_by_id('fix_upc_errors').click()

    """ User goes to view error detail."""
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 4

    browser.find_elements_by_tag_name('th')[1].text == 'UPC'
    browser.find_elements_by_tag_name('th')[2].text == 'Distributor'

    """ User deletes item """
    rows[1].find_elements_by_tag_name('td')[0].click()
    browser.find_element_by_id('delete').click()

    browser.get('http://localhost:3000/income/matching-errors')
    time.sleep(1)

    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3
    
    """ User deletes two items """
    rows[1].find_elements_by_tag_name('td')[0].click()
    rows[2].find_elements_by_tag_name('td')[0].click()
    browser.find_element_by_id('delete').click()

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to view imported income statements. """
    browser.find_element_by_id('view1').click()
    
    """ User goes to imported income statement detail to view summa to view summary."""
    time.sleep(1)
    assert browser.find_element_by_id('number_of_records').text == '31'



