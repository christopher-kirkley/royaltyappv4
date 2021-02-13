from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

import os

from royaltyapp.models import Artist

@pytest.fixture
def browser(db):
    browser = webdriver.Firefox()
    yield browser
    db.session.rollback()
    browser.quit()

def test_returns(browser, test_client, db):
    """ User goes to homepage """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'

    """ User uploads catalog and versions. """
    browser.find_element_by_id('catalog').click()
    time.sleep(1)
    browser.find_element_by_id('import_catalog').click()
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('catalog_upload').click()

    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('version_upload').click()

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
    upc.send_keys('999222')

    browser.find_element_by_id('add_version').click()
    browser.find_element_by_id('1').click()
    browser.find_element_by_id('add_version').click()
    browser.find_element_by_id('3').click()

    submit = browser.find_element_by_id('submit')
    submit.click()

    """ User sees Bundle item in table. """
    browser.find_element_by_id('bundle').click()
    bundle_table = browser.find_element_by_id('bundle_table')
    rows = bundle_table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'SS-3MYS'
    assert tds[1].text == 'Three Mystery Items'
    assert tds[2].text == 'SS-050cass SS-050lp'
    
    """ Navigate to bundle detail page. """
    bundle_detail = browser.find_element_by_id('bundle_detail')
    bundle_detail.click()
    assert browser.find_element_by_id('bundle_number').get_attribute("value") == 'SS-3MYS'
    assert browser.find_element_by_id('bundle_name').get_attribute("value") == 'Three Mystery Items'

    """ User edits bundle """
    browser.find_element_by_id('edit').click()

    upc = browser.find_element_by_name('upc')

    upc.clear()
    upc.send_keys('999111')

    browser.find_element_by_id('submit').click()
    
    """ Checks that bundles have been updated """
    browser.get('http://localhost:3000/bundle/1')
    time.sleep(1)
    upc = browser.find_element_by_name('upc')
    assert upc.get_attribute("value") == '999111'

    """ User goes to income. """
    browser.find_element_by_id('income').click()
    browser.find_element_by_id('income-data').text == 'No data'

    """ User goes to upload income. """
    browser.find_element_by_id('import_income').click()
    path = os.getcwd() + "/tests/files/bandcamp_test_3.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('upc_matching_errors').text == "You have 3 UPC matching errors."
    browser.find_element_by_id('fix_upc_errors').click()

    """ User use update function."""
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 4

    browser.find_elements_by_tag_name('th')[1].text == 'UPC'
    browser.find_elements_by_tag_name('th')[2].text == 'Distributor'

    """ Select first row. """
    rows[1].find_elements_by_tag_name('td')[0].click()

    """ Update type. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('SS-3MYS').click()
    browser.find_element_by_id('update').click()

    # # """ User matches version number. """
    # # table = browser.find_element_by_id('matching_error_table')
    # # rows = table.find_elements_by_tag_name('tr')
    # # assert len(rows) == 4
    
    browser.find_element_by_id('match').click()
    browser.find_element_by_id('column').click()
    browser.find_element_by_id('catalog_id').click()
    browser.find_element_by_id('BUNDLEERROR').click()
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('SS-3MYS').click()
    browser.find_element_by_id('submit').click()

    time.sleep(1)
    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to view imported income statements. """
    browser.find_element_by_id('view1').click()
    
    """ User goes to imported income statement detail to view summa to view summary."""
    time.sleep(1)
    assert browser.find_element_by_id('number_of_records').text == '6'


