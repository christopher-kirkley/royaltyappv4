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
    
    """ User navigates to catalog import page """
    browser.find_element_by_id('catalog').click()
    time.sleep(1)
    browser.find_element_by_id('import_catalog').click()

    """ User clicks to upload catalog. """
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    time.sleep(2)
    browser.find_element_by_id('catalog_upload').click()

    """ User returns to catalog and sees it has worked. """
    browser.find_element_by_id('catalog').click()
    catalog_table = browser.find_element_by_id('catalog_table')
    rows = catalog_table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'SS-050'
    assert tds[1].text == 'Ahmed Ag Kaedy'
    assert tds[2].text == 'Akaline Kidal'

    """ User uploads version CSV. """
    browser.find_element_by_id('import_catalog').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(2)
    browser.find_element_by_id('version_upload').click()
    
    """ User goes to Catalog Detail page and see the results. """
    browser.get('http://localhost:3000/catalog/1')
    time.sleep(2)
    version_number = browser.find_element_by_name('version[0].version_number')
    assert version_number.get_attribute("value") == 'SS-050cass'

    """ User uploads track CSV. """
    browser.find_element_by_id('catalog').click()
    browser.find_element_by_id('import_catalog').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/one_track.csv"
    browser.find_element_by_id('track_to_upload').send_keys(path)
    time.sleep(2)
    browser.find_element_by_id('track_upload').click()
    
    """ User goes to Catalog Detail page and see the results. """
    browser.get('http://localhost:3000/catalog/1')
    time.sleep(2)
    track_number = browser.find_element_by_name('track[0].track_number')
    assert track_number.get_attribute("value") == '1'
    
    time.sleep(1000)





    

