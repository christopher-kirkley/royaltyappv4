from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

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
    
    """ User navigates to artist page """
    artist = browser.find_element_by_id('artists')
    artist.click()

    """ User sees an empty table, clicks on button to add artist """
    assert browser.find_element_by_id("artist-table")
    add_artist = browser.find_element_by_id('add_artist')
    add_artist.click()
    time.sleep(1)

    """ User arrives at new page to add artist """
    artist_name = browser.find_element_by_id('artist_name')
    prenom = browser.find_element_by_id('prenom')
    surnom = browser.find_element_by_id('surnom')
    submit = browser.find_element_by_id('submit')

    artist_name.send_keys('Amanar')
    prenom.send_keys('Ahmed')
    surnom.send_keys('Ag Kaedi')
    submit.click()

    """ User can now see that artist was added. """
    table = browser.find_element_by_id('artist-table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(db.session.query(Artist).all()) == 1
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'Amanar'
    assert tds[1].text == 'Ahmed'
    assert tds[2].text == 'Ag Kaedi'

    """ User clicks on artist detail and goes to artist page """
    artist_detail = browser.find_element_by_id('artist-detail')
    artist_detail.click()
    assert browser.find_element_by_id('prenom')
    heading = browser.find_element_by_id('heading')
    assert heading.text == 'Artist Detail'
    assert browser.find_element_by_id('artist_name').get_attribute("value") == 'Amanar'
    assert browser.find_element_by_id('prenom').get_attribute("value") == 'Ahmed'
    assert browser.find_element_by_id('surnom').get_attribute("value") == 'Ag Kaedi'

    """ User realizes they made a mistake in the name,
    and updates spelling"""
    surnom = browser.find_element_by_id('surnom')
    surnom.clear()
    surnom.send_keys('Ag Kaedy')
    update = browser.find_element_by_id('update')
    update.click()
    assert browser.find_element_by_id('surnom').get_attribute("value") == 'Ag Kaedy'
    
    """ User returns to main page and verifies change."""
    artist = browser.find_element_by_id('artists')
    artist.click()
    time.sleep(1)
    table = browser.find_element_by_id('artist-table')
    rows = table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[2].text == 'Ag Kaedy'

    """ User goes to the catalog view """
    catalog = browser.find_element_by_id('catalog')
    catalog.click()
    assert browser.find_element_by_id('header').text == 'All Catalog'

    """ User clicks to add a new catalog item """
    add_catalog = browser.find_element_by_id('add-catalog-item')
    add_catalog.click()

    """ User fills out catalog info. """
    catalog_number = browser.find_element_by_id('catalog_number')
    catalog_number.send_keys('SS-050')
    catalog_name = browser.find_element_by_id('catalog_name')
    catalog_name.send_keys('Akaline Kidal')
    select = Select(browser.find_element_by_name('artist_id'))
    select.select_by_visible_text('Amanar')
    submit = browser.find_element_by_id('submit')
    submit.click()
    
    """ User sees Catalog item in table. """
    catalog = browser.find_element_by_id('catalog')
    catalog.click()
    catalog_table = browser.find_element_by_id('catalog_table')
    rows = catalog_table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'SS-050'
    assert tds[1].text == 'Amanar'
    assert tds[2].text == 'Akaline Kidal'
    
    """ Navigate to catalog detail page. """
    catalog_detail = browser.find_element_by_id('catalog_detail')
    catalog_detail.click()
    assert browser.find_element_by_id('catalog_number').get_attribute("value") == 'SS-050'
    assert browser.find_element_by_id('catalog_name').get_attribute("value") == 'Akaline Kidal'
    assert browser.find_element_by_id('artist_name').get_attribute("value") == '1'

    """ Click to add a version. """
    add_version = browser.find_element_by_id('add_version')
    add_version.click()
    version_number = browser.find_element_by_name('version[0].version_number')
    version_number.send_keys('SS-050lp')
    upc = browser.find_element_by_name('version[0].upc')
    upc.send_keys('123456')
    format = browser.find_element_by_name('version[0].format')
    format.send_keys('LP')
    version_name = browser.find_element_by_name('version[0].version_name')
    version_name.send_keys('Limited Edition Vinyl')
    submit = browser.find_element_by_id('submit')
    submit.click()
    version_number = browser.find_element_by_name('version[0].version_number')
    assert version_number.get_attribute("value") == 'SS-050lp'






