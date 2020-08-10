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
    msg = browser.find_element_by_id('msg')
    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('version_upload').click()
    msg = browser.find_element_by_id('version_msg')

    """ User goes to expense page and uploads a file."""
    browser.find_element_by_id('expense').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/expense_artist.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('artist_source').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)
    msg = browser.find_element_by_id('statement_message')
    assert msg.text == "Uploaded!"

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_artist.csv'
    
    """ User goes to expense page and uploads a second file."""
    browser.find_element_by_id('expense').click()
    time.sleep(1)
    path = os.getcwd() + "/tests/files/expense_catalog.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('catalog_source').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)
    msg = browser.find_element_by_id('statement_message')
    assert msg.text == "Uploaded!"

    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_artist.csv'

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('matching_errors').text == "You have 2 matching errors."
    browser.find_element_by_id('fix_errors').click()
    time.sleep(1)

    """ User loads matching error page. """
    assert browser.find_element_by_id('header').text == "Expense Matching Errors"
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    
    """ User updates type errors and submits. """
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('advance').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 10
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('recoupable').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 9
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('recoupable').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 8
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('recoupable').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 7
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('recoupable').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 6
    browser.find_element_by_id('new_expense_type').click()
    browser.find_element_by_id('recoupable').click()
    browser.find_element_by_id('type_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 5
    browser.find_element_by_id('artist_update').click()
    browser.find_element_by_id('artist_update').click()
    browser.find_element_by_id('catalog_update').click()
    browser.find_element_by_id('catalog_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1
    
    """ User goes to expense page and uploads a file."""
    browser.find_element_by_id('expense').click()
    time.sleep(1)
    browser.find_element_by_id('process_statements').click()

    """ User goes to view imported first income statement. """
    browser.find_element_by_id('view_imported_expense').click()
    time.sleep(1)
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    assert rows[1].find_elements_by_tag_name('td')[0].text == 'expense_catalog.csv'
    browser.find_element_by_id('1').click()
    assert browser.find_element_by_id('header').text == "Detail Imported Expense"
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 5

    """ User goes to second imported income statement. """
    browser.find_element_by_id('view_imported_expense').click()
    time.sleep(1)
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    assert rows[2].find_elements_by_tag_name('td')[0].text == 'expense_artist.csv'
    browser.find_element_by_id('2').click()
    assert browser.find_element_by_id('header').text == "Detail Imported Expense"
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 5

    """ User decides to go back and delete this statement. """
    browser.find_element_by_id('view_imported_expense').click()
    time.sleep(1)
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    rows[1].find_element_by_id("delete").click()

    """ Statement dissapears from page. """
    time.sleep(1)
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 2

    



