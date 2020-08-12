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
    path = os.getcwd() + "/tests/files/test1_catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    browser.find_element_by_id('catalog_upload').click()
    msg = browser.find_element_by_id('msg')
    path = os.getcwd() + "/tests/files/test1_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    browser.find_element_by_id('version_upload').click()
    msg = browser.find_element_by_id('version_msg')

    """ User uploads income file. """
    browser.find_element_by_id('income').click()
    path = os.getcwd() + "/tests/files/test1_bandcamp.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    browser.find_element_by_id('process_statements').click()

    """ User goes to expense file."""
    browser.find_element_by_id('expense').click()
    path = os.getcwd() + "/tests/files/test1_expense_artist.csv"
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

    """ User goes to view statement. """
    browser.find_element_by_id('statements_view').click()
    assert browser.find_element_by_id('header').text == 'View Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 2

    """ User navigates to first statement to view. """
    browser.find_element_by_id('1').click()
    assert browser.find_element_by_id('header').text == 'Statement'
