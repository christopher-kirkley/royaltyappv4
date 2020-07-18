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
    time.sleep(2)
    browser.find_element_by_id('catalog_upload').click()
    msg = browser.find_element_by_id('msg')
    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(2)
    browser.find_element_by_id('version_upload').click()
    msg = browser.find_element_by_id('version_msg')

    """ User goes to income page and uploads a file."""
    browser.find_element_by_id('income').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/bandcamp_test.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    
    # select = Select(browser.find_element_by_id('source_statement'))
    # select.select_by_visible_text('Bandcamp')
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)
    msg = browser.find_element_by_id('statement_message')
    assert msg.text == "Uploaded!"

    """ User sees prompt for errors, and clicks to fix matching errors. """
    # assert browser.find_element_by_id('error_msg').text != "Error!"
    assert browser.find_element_by_id('matching_errors').text == "You have 732 matching errors."
    browser.find_element_by_id('fix_errors').click()
    time.sleep(1)

    """ User loads matching error page. """
    assert browser.find_element_by_id('header').text == "Matching Errors"
    

