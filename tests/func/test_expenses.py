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

    """ Select all rows. """
    main = rows[0].find_elements_by_tag_name('th')[0].click()

    """ Update artist. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id(1).click()
    browser.find_element_by_id('update').click()

    """ Returns to expense page."""
    assert browser.find_element_by_id("header").text == 'Expense Import'

    """ User fixes type matching errors. """
    browser.find_element_by_id('fix_type_errors').click()

    """ User sees error table. """
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 7

    rows[0].find_elements_by_tag_name('th')[1].text == 'Date'

    tds = rows[1].find_elements_by_tag_name('td')

    assert tds[1].text == '2019-07-26' 
    assert tds[2].text == 'Xoom.com' 

    """ Select all rows. """
    main = rows[0].find_elements_by_tag_name('th')[0].click()

    """ Update type. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id(1).click()
    browser.find_element_by_id('update').click()

    """ Returns to expense page."""
    assert browser.find_element_by_id("header").text == 'Expense Import'

    """ User fixes catalog matching errors. """
    browser.find_element_by_id('fix_catalog_errors').click()

    """ User sees error table. """
    table = browser.find_element_by_id('matching_error_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 3

    rows[0].find_elements_by_tag_name('th')[1].text == 'Date'

    tds = rows[1].find_elements_by_tag_name('td')

    assert tds[1].text == '2019-07-20' 
    assert tds[2].text == 'A to Z' 

    """ Select all rows. """
    main = rows[0].find_elements_by_tag_name('th')[0].click()

    """ Update catalog. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id(1).click()
    browser.find_element_by_id('update').click()

    """ Returns to expense page."""
    assert browser.find_element_by_id("header").text == 'Expense Import'

    """ Process errors."""
    browser.find_element_by_id('process_errors').click()

    """ User goes to view imported expense statements. """
    assert browser.find_element_by_id('header').text == 'Expense'
    
    time.sleep(1)
    table = browser.find_element_by_id('imported_expense_table')
    rows = table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td')
    assert tds[0].text == 'expense_catalog.csv'
    assert tds[1].text == '2019-07-20'
    assert tds[2].text == '2019-11-26'

    browser.find_element_by_id('view1').click()

    time.sleep(1000)
    
    """ User goes to imported expense statement detail to view summa to view summary."""
    time.sleep(1)
    assert browser.find_element_by_id('number_of_records').text == '4'

    """ User decides to go back and delete this statement. """
    browser.get('http://localhost:3000/income')
    time.sleep(1)
    browser.find_element_by_id("delete1").click()
