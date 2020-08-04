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

    """ User goes to expense page and uploads a file."""
    browser.find_element_by_id('expense').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/expense_catalog.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)
    msg = browser.find_element_by_id('statement_message')
    assert msg.text == "Uploaded!"

    # """ User sees prompt for errors, and clicks to fix matching errors. """
    # assert browser.find_element_by_id('matching_errors').text == "You have 1 matching errors."
    # browser.find_element_by_id('fix_errors').click()
    # time.sleep(1)

    # """ User loads matching error page. """
    # assert browser.find_element_by_id('header').text == "Matching Errors"
    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # tds = rows[1].find_elements_by_tag_name('td');
    # assert tds[0].text == 'bandcamp'
    # assert tds[1].text == ''
    # assert tds[2].text == 'SS-050-cass'
    # assert tds[3].text == 'SS-050'
    
    # """ User fixes errors and submits. """
    # browser.find_element_by_id('new_upc').click()
    # browser.find_element_by_id('SS-050cass').click()
    # browser.find_element_by_id('update').click()
    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # assert len(rows) == 1

    # """ User checks another test file. """
    # browser.find_element_by_id('income').click()
    # time.sleep(1)
    # path = os.getcwd() + "/tests/files/bandcamp_test_2.csv"
    # browser.find_element_by_id('select_statement').send_keys(path)
    # browser.find_element_by_id('source_statement').click()
    # browser.find_element_by_id('bandcamp').click()
    # browser.find_element_by_id('upload_statement').click()
    # time.sleep(1)

    # """ User sees statement added to the list of pending statements. """
    # pending_statement = browser.find_element_by_id('pending_statement')
    # assert pending_statement.text == 'bandcamp_test_2.csv'
    
    # """ User sees prompt for errors, and clicks to fix matching errors. """
    # assert browser.find_element_by_id('matching_errors').text == "You have 4 matching errors."
    # browser.find_element_by_id('fix_errors').click()

    # """ User updates version number. """
    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # rows[1].find_element_by_id('version_number').click()
    # browser.find_element_by_id('new_upc').click()
    # browser.find_element_by_id('SS-050cass').click()
    # browser.find_element_by_id('update').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # assert len(rows) == 3

    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # rows[1].find_element_by_id('medium').click()
    # browser.find_element_by_id('SS-050cass').click()
    # browser.find_element_by_id('update').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('matching_error_table')
    # rows = table.find_elements_by_tag_name('tr')
    # assert len(rows) == 2

    # """ User returns to page and tries to process payments. """
    # browser.find_element_by_id('income').click()
    # time.sleep(1)
    # browser.find_element_by_id('process_statements').click()
    # time.sleep(1)

    # """ User goes to view imported income statements. """
    # browser.find_element_by_id('view_imported_income').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('imported_income_table')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_elements_by_tag_name('td')[0].text == 'bandcamp_test_2.csv'
    # browser.find_element_by_id('1').click()
    
    # """ User goes to imported income statement detail to view summa to view summary."""
    # time.sleep(1)
    # assert browser.find_element_by_id('statement_summary')
    # assert browser.find_element_by_id('number_of_records').text == '4'

    # """ User decides to go back and delete this statement. """
    # browser.find_element_by_id('view_imported_income').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('imported_income_table')
    # rows = table.find_elements_by_tag_name('tr')
    # rows[1].find_element_by_id("delete").click()

    # """ Statement dissapears from page. """
    # time.sleep(1)
    # table = browser.find_element_by_id('imported_income_table')
    # rows = table.find_elements_by_tag_name('tr')
    # assert len(rows) == 1

    # """ User navigates to add Expenses. """
    # time.sleep(3000)
    



