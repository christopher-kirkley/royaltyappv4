from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

import os

from royaltyapp.models import Artist

base = os.path.basename(__file__)
CASE = base.split('.')[0]

@pytest.fixture
def browser(db):
    browser = webdriver.Firefox()
    yield browser
    db.session.rollback()
    browser.quit()

def import_catalog(browser, test_client, db):
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

def test_returns(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'
    
    import_catalog(browser, test_client, db)

    """ User goes to income. """
    browser.find_element_by_id('income').click()

    """ User goes to upload income. """
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + f"/tests/func/{CASE}/bandcamp.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('refund_matching_errors').text == "You have 2 refund errors."
    browser.find_element_by_id('fix_refund_errors').click()

    """ User goes to view error detail."""
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    browser.find_elements_by_tag_name('th')[0].text == 'Order ID'
    browser.find_elements_by_tag_name('th')[1].text == 'UPC'
    browser.find_elements_by_tag_name('th')[2].text == 'Distributor'

    """ User selects item """
    rows[1].find_elements_by_tag_name('td')[0].click()

    amount = browser.find_element_by_id('new_value')
    amount.click()
    amount.send_keys('-3')

    browser.find_element_by_id('update').click()

    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    rows[1].find_elements_by_tag_name('td')[0].click()

    amount = browser.find_element_by_id('new_value')
    amount.click()
    amount.send_keys('-3')

    browser.find_element_by_id('update').click()

    time.sleep(1)

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to view imported income statements. """
    browser.find_element_by_id('view1').click()
    
    """ User goes to imported income statement detail to view summa to view summary."""
    time.sleep(1)
    assert browser.find_element_by_id('number_of_records').text == '4'



