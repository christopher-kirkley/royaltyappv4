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
    path = os.getcwd() + "/tests/files/catalog.csv"
    browser.find_element_by_id('catalog_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('catalog_upload').click()

    path = os.getcwd() + "/tests/files/versions.csv"
    browser.find_element_by_id('version_to_upload').send_keys(path)
    time.sleep(1)
    browser.find_element_by_id('version_upload').click()

    """ User goes to income. """
    browser.find_element_by_id('income').click()
    browser.find_element_by_id('income-data').text == 'No data'

    """ User goes to upload income. """
    browser.find_element_by_id('import_income').click()

    """ Uploads Bandcamp """
    path = os.getcwd() + "/tests/files/scenario1/20200101-20200131_bandcamp_raw_data_Sahel-Sounds.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('bandcamp').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(1)

    """ Uploads Shopify """
    path = os.getcwd() + "/tests/files/scenario1/sales_2020-01-01_2020-01-31.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('shopify').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(5)

    """ Uploads SD Digital """
    path = os.getcwd() + "/tests/files/scenario1/SS013120digpd.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('sddigital').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(10)

    """ Uploads SD Physical """
    path = os.getcwd() + "/tests/files/scenario1/SS013120physpd.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('sdphysical').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(5)

    """ Uploads SDS """
    path = os.getcwd() + "/tests/files/scenario1/Sahel_Sounds_202001_DSR.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('sds').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(5)

    """ Uploads Quickbooks (User generated) """
    path = os.getcwd() + "/tests/files/scenario1/qb_sales_2020A.csv"
    browser.find_element_by_id('file_upload').send_keys(path)
    browser.find_element_by_id('source_statement').click()
    browser.find_element_by_id('quickbooks').click()
    browser.find_element_by_id('upload_statement').click()
    time.sleep(5)

    time.sleep(10000)

    """ User sees prompt for errors, and clicks to fix matching errors. """
    browser.find_element_by_id('fix_isrc_errors').click()

    """ Select first row. """
    browser.find_element_by_xpath('//table/thead/tr[1]/th[1]/div/input').click()

    """ Update type. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('1').click()
    browser.find_element_by_id('update').click()

    """ User sees prompt for errors, and clicks to fix matching errors. """
    assert browser.find_element_by_id('upc_matching_errors').text == "You have 4 UPC matching errors."
    browser.find_element_by_id('fix_upc_errors').click()

    """ Select first row. """
    browser.find_element_by_xpath('//table/thead/tr[1]/th[1]/div/input').click()

    """ Update type. """
    browser.find_element_by_id('new_value').click()
    browser.find_element_by_id('SS-050lp').click()
    browser.find_element_by_id('update').click()

    time.sleep(1)

    """ Process payments. """
    browser.find_element_by_id('process_errors').click()

    """ User goes to generate statement. """
    browser.find_element_by_id('statements').click()
    browser.find_element_by_id('generate').click()
    assert browser.find_element_by_id('header').text == 'Generate Statement'
    
    """ Define statement. """
    start_date = browser.find_element_by_id('start-date')
    start_date.click()
    start_date.send_keys('01012020')

    end_date = browser.find_element_by_id('end-date')
    end_date.click()
    end_date.send_keys('01312020')

    browser.find_element_by_id('previous_balance_id').click()
    time.sleep(1)
    browser.find_element_by_id('none').click()
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    """ User goes to view statement. """
    assert browser.find_element_by_id('header').text == 'Statements'
    table = browser.find_element_by_id('statement_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(rows) == 1

    """ User navigates to first statement to view main statement."""
    browser.find_element_by_id('1').click()
    time.sleep(2)
    assert browser.find_element_by_id('header').text == 'Statement Summary'
    assert browser.find_element_by_id('statement-name').text == 'statement_2020_01_01_2020_01_31'
    assert browser.find_element_by_id('current-owed').text == 'Current Owed: $0'

    # """ User navigates to artist statement detail. """
    # browser.find_element_by_id('1').click()
    # assert browser.find_element_by_id('header').text == 'Statement Detail'
    # time.sleep(1)
    # table = browser.find_element_by_id('artist-statement-income')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('catalog_name').text == 'Akaline Kidal'
    # assert rows[1].find_element_by_id('digital_net').text == '0'
    # assert rows[1].find_element_by_id('physical_net').text == '30.45'
    # assert rows[1].find_element_by_id('combined_net').text == '30.45'

    # table = browser.find_element_by_id('artist-statement-expense')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('date').text == '2020-01-01'

    # table = browser.find_element_by_id('artist-statement-advance')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('date').text == '2020-01-01'

    # table = browser.find_element_by_id('album-sales')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('catalog_name').text == 'Akaline Kidal'

    # table = browser.find_element_by_id('track-sales')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('track_name').text == 'Adounia'

    # table = browser.find_element_by_id('artist-statement-summary')

    # """ User goes to edit statement. """
    # browser.find_element_by_id('statements_view').click()
    # browser.find_element_by_id('edit').click()
    # assert browser.find_element_by_id('header').text == 'Edit Statement'

    # time.sleep(2)
    # table = browser.find_element_by_id('edit-statement')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('version_number').text == 'SS-050cass'
    
    # rows[1].find_element_by_id('1').click()
    # time.sleep(1)
    # table = browser.find_element_by_id('edit-statement')
    # rows = table.find_elements_by_tag_name('tr')
    # assert rows[1].find_element_by_id('version_number').text == 'SS-050digi'

    # browser.find_element_by_id('update').click()

    # """ User returns to statement and sees it has been updated. """
    
    


    
