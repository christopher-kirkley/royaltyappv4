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

    """ User fills out catalog info. """
    bundle_number = browser.find_element_by_id('bundle_number')
    bundle_number.send_keys('SS-3MYS')
    bundle_name = browser.find_element_by_id('bundle_name')
    bundle_name.send_keys('Three Mystery Items')

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
    assert tds[2].text == 'SS-050cass'
    
    # """ Navigate to catalog detail page. """
    # catalog_detail = browser.find_element_by_id('catalog_detail')
    # catalog_detail.click()
    # assert browser.find_element_by_id('catalog_number').get_attribute("value") == 'SS-050'
    # assert browser.find_element_by_id('catalog_name').get_attribute("value") == 'Akaline Kidal'
    # assert browser.find_element_by_id('artist_name').get_attribute("value") == '1'
    # # """ User goes to income. """
    # # browser.find_element_by_id('income').click()
    # # browser.find_element_by_id('income-data').text == 'No data'

    # # """ User goes to upload income. """
    # # browser.find_element_by_id('import_income').click()
    # # path = os.getcwd() + "/tests/files/bandcamp_test_2.csv"
    # # browser.find_element_by_id('file_upload').send_keys(path)
    # # browser.find_element_by_id('source_statement').click()
    # # browser.find_element_by_id('bandcamp').click()
    # # browser.find_element_by_id('upload_statement').click()
    # # time.sleep(1)

    # # """ User sees statement added to the list of pending statements. """
    # # pending_statement = browser.find_element_by_id('pending_statement')
    # # assert pending_statement.text == 'bandcamp_test_2.csv'

    # # """ Upload a second statement. """
    # # path = os.getcwd() + "/tests/files/bandcamp_test.csv"
    # # browser.find_element_by_id('file_upload').send_keys(path)
    # # browser.find_element_by_id('source_statement').click()
    # # browser.find_element_by_id('bandcamp').click()
    # # browser.find_element_by_id('upload_statement').click()
    # # time.sleep(1)

    # # """ User deletes uploaded second statement. """
    # # browser.find_element_by_id('delete-0').click()
    # # time.sleep(1)

    # # """ User sees prompt for errors, and clicks to fix matching errors. """
    # # assert browser.find_element_by_id('isrc_matching_errors').text == "You have 2 ISRC matching errors."
    # # browser.find_element_by_id('fix_isrc_errors').click()

    # # """ User use update function."""
    # # table = browser.find_element_by_id('matching_error_table')
    # # rows = table.find_elements_by_tag_name('tr')
    # # assert len(rows) == 3
    # # assert browser.find_element_by_xpath('//table/thead/tr[1]/th[2]').text == 'ISRC'
    # # assert browser.find_element_by_xpath('//table/thead/tr[1]/th[3]').text == 'Distributor'

    # # """ Select first row. """
    # # browser.find_element_by_xpath('//table/tbody/tr[1]/td[1]/div/input').click()

    # # """ Update type. """
    # # browser.find_element_by_id('new_value').click()
    # # browser.find_element_by_id('1').click()
    # # browser.find_element_by_id('update').click()

    # # """ User matches version number. """
    # # table = browser.find_element_by_id('matching_error_table')
    # # rows = table.find_elements_by_tag_name('tr')
    # # assert len(rows) == 2

    # # browser.find_element_by_id('match').click()
    # # browser.find_element_by_id('column').click()
    # # browser.find_element_by_id('isrc_id').click()
    # # browser.find_element_by_id('missingisrc').click()
    # # browser.find_element_by_id('new_value').click()
    # # browser.find_element_by_id('QZDZE1905001').click()
    # # browser.find_element_by_id('submit').click()

    # # time.sleep(1)
    # # """ User sees prompt for errors, and clicks to fix matching errors. """
    # # assert browser.find_element_by_id('upc_matching_errors').text == "You have 4 UPC matching errors."
    # # browser.find_element_by_id('fix_upc_errors').click()

    # # """ User use update function."""
    # # table = browser.find_element_by_id('matching_error_table')
    # # rows = table.find_elements_by_tag_name('tr')
    # # assert len(rows) == 5

    # # browser.find_elements_by_tag_name('th')[1].text == 'UPC'
    # # browser.find_elements_by_tag_name('th')[2].text == 'Distributor'

    # # tds = rows[1].find_elements_by_tag_name('td')

    # # assert tds[1].text == 'missingupc' 
    # # assert tds[2].text == 'bandcamp' 

    # # """ Select first row. """
    # # rows[1].find_elements_by_tag_name('td')[0].click()

    # # """ Update type. """
    # # browser.find_element_by_id('new_value').click()
    # # browser.find_element_by_id('SS-050lp').click()
    # # browser.find_element_by_id('update').click()

    # # """ User matches version number. """
    # # table = browser.find_element_by_id('matching_error_table')
    # # rows = table.find_elements_by_tag_name('tr')
    # # assert len(rows) == 4
    
    # # browser.find_element_by_id('match').click()
    # # browser.find_element_by_id('column').click()
    # # browser.find_element_by_id('upc_id').click()
    # # browser.find_element_by_id('missingupc').click()
    # # browser.find_element_by_id('new_value').click()
    # # browser.find_element_by_id('SS-050cass').click()
    # # browser.find_element_by_id('submit').click()

    # # time.sleep(1)
    # # """ Process payments. """
    # # browser.find_element_by_id('process_errors').click()

    # # """ User goes to view imported income statements. """
    # # browser.find_element_by_id('view1').click()
    
    # # """ User goes to imported income statement detail to view summa to view summary."""
    # # time.sleep(1)
    # # assert browser.find_element_by_id('number_of_records').text == '6'

    # # """ User decides to go back and delete this statement. """
    # # browser.get('http://localhost:3000/income')
    # # time.sleep(1)
    # # browser.find_element_by_id("delete1").click()

