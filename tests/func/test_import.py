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
    path = os.getcwd() + "/tests/files/full_catalog.csv"
    browser.find_element_by_id('file_to_upload').send_keys(path)
    time.sleep(2)
    browser.find_element_by_id('submit').click()
    msg = browser.find_element_by_id('msg')
    assert msg.text == '1 file uploaded'

    """ User returns to catalog and sees it has worked. """
    browser.find_element_by_id('catalog').click()
    time.sleep(1)
    catalog_table = browser.find_element_by_id('catalog_table')
    rows = catalog_table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'SS-050'
    assert tds[1].text == 'Amanar'
    assert tds[2].text == 'Akaline Kidal'
    

    

