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
    
    """ User navigates to view artist page """
    artist = browser.find_element_by_id('artists')
    artist.click()

    """ User sees an empty table, clicks on button to add artist """
    assert browser.find_element_by_id("artists-data").text == 'No data'
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
    heading = browser.find_element_by_id('header')
    assert heading.text == 'Artist Detail'
    assert browser.find_element_by_id('artist_name').get_attribute("value") == 'Amanar'
    assert browser.find_element_by_id('prenom').get_attribute("value") == 'Ahmed'
    assert browser.find_element_by_id('surnom').get_attribute("value") == 'Ag Kaedi'

    """ User realizes they made a mistake in the name,
    and updates spelling"""
    browser.find_element_by_id('edit').click()

    surnom = browser.find_element_by_id('surnom')
    surnom.clear()
    surnom.send_keys('Ag Kaedy')
    submit = browser.find_element_by_id('submit')
    submit.click()
    
    """ User returns to main page and verifies change."""
    table = browser.find_element_by_id('artist-table')
    rows = table.find_elements_by_tag_name('tr')
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[2].text == 'Ag Kaedy'

    """ User goes to the catalog view """
    browser.find_element_by_id('catalog').click()

    assert browser.find_element_by_id('header').text == 'Catalog Items'

    """ User clicks to add a new catalog item """
    add_catalog = browser.find_element_by_id('add_catalog')
    add_catalog.click()

    """ User fills out catalog info. """
    catalog_number = browser.find_element_by_id('catalog_number')
    catalog_number.send_keys('SS-050')
    catalog_name = browser.find_element_by_id('catalog_name')
    catalog_name.send_keys('Akaline Kidal')

    browser.find_element_by_id('artist_name').click()
    browser.find_element_by_id('1').click()

    submit = browser.find_element_by_id('submit')
    submit.click()

    """ User sees Catalog item in table. """
    browser.find_element_by_id('catalog').click()
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
    browser.find_element_by_id('edit').click()

    add_version = browser.find_element_by_id('add_version')
    add_version.click()
    version_number = browser.find_element_by_name('newVersion[0].version_number')
    version_number.send_keys('SS-050lp')
    upc = browser.find_element_by_name('newVersion[0].upc')
    upc.send_keys('123456')
    format = browser.find_element_by_name('newVersion[0].format')
    format.send_keys('LP')
    version_name = browser.find_element_by_name('newVersion[0].version_name')
    version_name.send_keys('Limited Edition Vinyl')

    """ Adds another version """
    browser.find_element_by_id('add_version').click()

    version_number = browser.find_element_by_name('newVersion[1].version_number')
    version_number.send_keys('SS-050cd')
    upc = browser.find_element_by_name('newVersion[1].upc')
    upc.send_keys('678910')
    format = browser.find_element_by_name('newVersion[1].format')
    format.send_keys('CD')
    version_name = browser.find_element_by_name('newVersion[1].version_name')
    version_name.send_keys('Limited Edition CD')

    browser.find_element_by_id('submit').click()

    browser.get('http://localhost:3000/catalog/1')
    time.sleep(1)
    version_number = browser.find_element_by_name('version[1].version_number')
    assert version_number.get_attribute("value") == 'SS-050cd'

    """ User goes to edit versions """
    browser.find_element_by_id('edit').click()

    upc = browser.find_element_by_name('version[0].upc')
    version_number = browser.find_element_by_name('version[0].version_number')
    version_name = browser.find_element_by_name('version[0].version_name')
    format = browser.find_element_by_name('version[0].format')

    upc.clear()
    upc.send_keys('11111')
    version_number.clear()
    version_number.send_keys('SS-050cass')
    version_name.clear()
    version_name.send_keys('Limited Cassette')
    format.clear()
    format.send_keys('Cassette')

    browser.find_element_by_id('submit').click()
    
    """ Checks that versions have been updated """
    browser.get('http://localhost:3000/catalog/1')
    time.sleep(1)
    upc = browser.find_element_by_name('version[0].upc')
    assert upc.get_attribute("value") == '11111'

    """ User goes to edit tracks. """
    browser.find_element_by_id('edit').click()

    """ Adds some tracks. """
    add_track = browser.find_element_by_id('add_track')
    add_track.click()
    track_name = browser.find_element_by_name('newTrack[0].track_name')
    track_name.send_keys('Tacos for Sale')
    isrc = browser.find_element_by_name('newTrack[0].isrc')
    isrc.send_keys('qwerty123')
    select = Select(browser.find_element_by_name('artist_id'))
    select.select_by_visible_text('Amanar')

    browser.find_element_by_id('submit').click()
    
    browser.get('http://localhost:3000/catalog/1')
    time.sleep(1)
    track_number = browser.find_element_by_name('track[0].track_number')
    track_name = browser.find_element_by_name('track[0].track_name')
    isrc = browser.find_element_by_name('track[0].isrc')
    artist = browser.find_element_by_name('track[0].artist_id')
    track_id = browser.find_element_by_name('track[0].id')
    assert track_number.get_attribute("value") == '1'
    assert track_name.get_attribute("value") == 'Tacos for Sale'
    assert isrc.get_attribute("value") == 'qwerty123'
    assert artist.get_attribute("value") == '1'
    assert track_id.get_attribute("value") == '1'

    """ User goes to edit tracks. """
    browser.find_element_by_id('edit').click()

    add_track = browser.find_element_by_id('add_track')
    add_track.click()
    track_name = browser.find_element_by_name('newTrack[0].track_name')
    track_name.send_keys('Burritos for Rent')
    isrc = browser.find_element_by_name('newTrack[0].isrc')
    isrc.send_keys('uiop1234')
    select = Select(browser.find_element_by_name('artist_id'))
    select.select_by_visible_text('Amanar')

    browser.find_element_by_id('submit').click()

    browser.get('http://localhost:3000/catalog/1')
    time.sleep(1)
    track_number = browser.find_element_by_name('track[1].track_number')
    track_name = browser.find_element_by_name('track[1].track_name')
    isrc = browser.find_element_by_name('track[1].isrc')
    artist = browser.find_element_by_name('track[1].artist_id')
    assert track_number.get_attribute("value") == '2'
    assert track_name.get_attribute("value") == 'Burritos for Rent'
    assert isrc.get_attribute("value") == 'uiop1234'
    assert artist.get_attribute("value") == '1'


    """ User edits the first track and changes the name. """
    browser.find_element_by_id('edit').click()

    track_name = browser.find_element_by_name('track[0].track_name')
    track_name.clear()
    track_name.send_keys('Tacos for President')

    isrc = browser.find_element_by_name('track[0].isrc')
    isrc.clear()
    isrc.send_keys('1800beansforsale')

    browser.find_element_by_id('submit').click()

    browser.get('http://localhost:3000/catalog/1')
    time.sleep(1)
    track_name = browser.find_element_by_name('track[0].track_name')
    assert track_name.get_attribute("value") == 'Tacos for President'
    isrc = browser.find_element_by_name('track[0].isrc')
    assert isrc.get_attribute("value") == '1800beansforsale'

    

    

