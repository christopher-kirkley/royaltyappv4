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

    """ User goes to expense. """
    browser.find_element_by_id('expense').click()
    browser.find_element_by_id('expense-data').text == 'No data'

    """ User goes to upload income. """
    browser.find_element_by_id('import_expense').click()

    """ User selects first file. """
    path = os.getcwd() + "/tests/files/expense_artist.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('artist_source').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_artist.csv'
    
    """ User uploads a second file."""
    path = os.getcwd() + "/tests/files/expense_catalog.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('catalog_source').click()
    browser.find_element_by_id('upload_statement').click()

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_artist.csv'

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('artist_matching_errors').text == "You have 2 artist matching errors."

    assert browser.find_element_by_id('catalog_matching_errors').text == "You have 2 catalog matching errors."

    assert browser.find_element_by_id('type_matching_errors').text == "You have 6 type matching errors."

    """ User fixes artist matching errors. """
    browser.find_element_by_id('fix_artist_errors').click()

    """ User sees error table. """
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    rows[0].find_elements_by_tag_name('th')[1].text == 'Date'

    tds = rows[1].find_elements_by_tag_name('td')

    assert tds[1].text == '2019-07-17' 
    assert tds[2].text == 'Les Filles de Illighadad' 

    browser.find_element_by_id('match').click()
    browser.find_element_by_id('column').click()
    time.sleep(1000)
    browser.find_element_by_id('upc_id').click()
    browser.find_element_by_id('missingupc').click()
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('SS-050cass').click()
    browser.find_element_by_id('submit').click()
    



