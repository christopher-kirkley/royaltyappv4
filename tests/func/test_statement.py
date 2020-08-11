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
    browser.find_element_by_id('import_catalog').click()
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    browser.find_element_by_id('catalog_upload').click()
    msg = browser.find_element_by_id('msg')
    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    browser.find_element_by_id('version_upload').click()
    msg = browser.find_element_by_id('version_msg')

    """ User uploads income file. """
    browser.find_element_by_id('income').click()
    path = os.getcwd() + "/tests/files/bandcamp_test_2.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    browser.find_element_by_id('process_statements').click()

    """ User goes to expense file."""
    browser.find_element_by_id('expense').click()
    path = os.getcwd() + "/tests/files/expense_artist.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('artist_source').click()
    browser.find_element_by_id('upload_statement').click()
    msg = browser.find_element_by_id('statement_message')
    browser.find_element_by_id('process_statements').click()

    """ User goes to generate statement. """
    browser.find_element_by_id('statements_generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    browser.find_element_by_id('previous_balance_id').click()
    browser.find_element_by_id('None').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)
    assert browser.find_element_by_id('message').text == 'Uploaded!'
    
