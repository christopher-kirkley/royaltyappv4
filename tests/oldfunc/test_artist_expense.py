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
    browser.find_element_by_id('import').click()
    path = os.getcwd() + "/tests/files/one_catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    browser.find_element_by_id('catalog_upload').click()
    msg = browser.find_element_by_id('msg')
    path = os.getcwd() + "/tests/files/one_version.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    browser.find_element_by_id('version_upload').click()
    msg = browser.find_element_by_id('version_msg')

    """ User goes to expense page and uploads a file."""
    browser.find_element_by_id('expense').click()
    browser.find_element_by_id('import_expense').click()
    path = os.getcwd() + "/tests/files/expense_artist.csv"
    browser.find_element_by_id('select_statement').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('artist_source').click()
    browser.find_element_by_id('upload_statement').click()
    
    """ User sees statement added to the list of pending statements. """
    pending_statement = browser.find_element_by_id('pending_statement')
    assert pending_statement.text == 'expense_artist.csv'
    
    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('matching_errors').text == "You have 6 matching errors."
    browser.find_element_by_id('fix_errors').click()

    """ User loads matching error page. """
    assert browser.find_element_by_id('header').text == "Expense Matching Errors"
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'Les Filles de Illighadad'
    assert tds[1].text == ''
    assert tds[2].text == '10% of Tour – paid out of tour money'
    assert tds[3].text == 'Payout'
    
    """ User updates artist errors and submits. """
    browser.find_element_by_id('new_artist').click()
    browser.find_element_by_id('Ahmed Ag Kaedy').click()
    browser.find_element_by_id('artist_update').click()
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 6

    time.sleep(1000)
    
    """Finish"""

    # """ User checks another test file. """
    # browser.find_element_by_id('income').click()
    # time.sleep(1)
    # path = os.getcwd() + "/tests/files/bandcamp_test_2.csv"
    # browser.find_element_by_id('select_statement').send_keys(path)
    # browser.find_element_by_id('source_statement').click()
    # browser.find_element_by_id('bandcamp').click()
    # browser.find_element_by_id('upload_statement').click()
    # time.sleep(1)

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
    



