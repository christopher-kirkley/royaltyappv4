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

    """ User checks another test file. """
    browser.find_element_by_id('income').click()
    browser.find_element_by_id('import_income').click()

    path = os.getcwd() + "/tests/files/sd_digital_test1.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('sddigital').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)
    
    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'sd_digital_test1.csv'

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('matching_errors').text == "You have 1 matching errors."
    browser.find_element_by_id('fix_errors').click()
    

    """ User matches version number. """
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 5
    

    browser.find_element_by_id('match').click()

    browser.find_element_by_id('column').click()
    browser.find_element_by_id('missingupc').click()
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('SS-050cass').click()
    browser.find_element_by_id('submit').click()

    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to view imported income statements. """
    table = browser.find_element_by_id('income_table')
    rows = table.find_elements_by_tag_name('tr')
    assert rows[1].find_elements_by_tag_name('td')[0].text == 'bandcamp_test_2.csv'
    browser.find_element_by_id('view1').click()
    
    """ User goes to imported income statement detail to view summa to view summary."""
    time.sleep(1)
    assert browser.find_element_by_id('number_of_records').text == '4'

    """ User decides to go back and delete this statement. """
    browser.get('http://localhost:3000/income')
    time.sleep(1)
    browser.find_element_by_id("delete1").click()

    """ Statement dissapears from page. """


    



