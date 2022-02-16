from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json
import os

import time

from royaltyapp.models import Artist, add_admin_user

from helpers import login

base = os.path.basename(__file__)
CASE = base.split('.')[0]

@pytest.fixture
def browser(db):
    browser = webdriver.Firefox()
    add_admin_user(db)
    yield browser
    db.session.rollback()
    browser.quit()

def test_returns(browser, test_client, db):
    login(browser)
    
    """ User navigates to view artist page """
    artist = browser.find_element_by_id('artists')
    artist.click()

    """ User sees an empty table, clicks on button to add artist """
    assert browser.find_element_by_id("artists-data").text == 'No data'
    add_artist = browser.find_element_by_id('add_artist')
    add_artist.click()
    
    """ User arrives at new page to add artist """
    artist_name = browser.find_element_by_id('artist_name')
    prenom = browser.find_element_by_id('prenom')
    surnom = browser.find_element_by_id('surnom')

    browser.find_element_by_id('contact_id').click()
    browser.find_element_by_id('new').click()
    contact_prenom = browser.find_element_by_id('new_contact_prenom')
    contact_middle = browser.find_element_by_id('new_contact_middle')
    contact_surnom = browser.find_element_by_id('new_contact_surnom')
    address = browser.find_element_by_id('new_address')
    phone = browser.find_element_by_id('new_phone')
    bank_name = browser.find_element_by_id('new_bank_name')
    bban = browser.find_element_by_id('new_bban')
    notes = browser.find_element_by_id('new_notes')

    submit = browser.find_element_by_id('submit')

    artist_name.send_keys('Fishstick')
    prenom.send_keys('Bob')
    surnom.send_keys('Nono')

    contact_prenom.send_keys('Bob')
    contact_middle.send_keys('Bo')
    contact_surnom.send_keys('Nono')
    address.send_keys('100 Main, Bamako, Mali')
    phone.send_keys('+22323214124')
    bank_name.send_keys('Bank of World')
    bban.send_keys('ML25252362346345')
    notes.send_keys('Wire')

    submit.click()

    """ User can now see that artist was added. """
    table = browser.find_element_by_id('artist-table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(db.session.query(Artist).all()) == 1
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'Fishstick'
    assert tds[1].text == 'Bob Bo Nono'

    """ Go to catalog page """
    browser.find_element_by_id('catalog').click()

    """ User clicks to add a new catalog item """
    add_catalog = browser.find_element_by_id('add_catalog')
    add_catalog.click()

    """ User fills out catalog info. """
    catalog_number = browser.find_element_by_id('catalog_number')
    catalog_number.send_keys('TEST-01')
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
    assert tds[0].text == 'TEST-01'
    assert tds[1].text == 'Fishstick'
    assert tds[2].text == 'Akaline Kidal'
    
    """ Navigate to catalog detail page. """
    catalog_detail = browser.find_element_by_id('catalog_detail')
    catalog_detail.click()
    assert browser.find_element_by_id('catalog_number').get_attribute("value") == 'TEST-01'
    assert browser.find_element_by_id('catalog_name').get_attribute("value") == 'Akaline Kidal'
    assert browser.find_element_by_id('artist_name').get_attribute("value") == '1'

    """ Clicks to add image """
    browser.find_element_by_id('edit').click()
    path = os.getcwd() + f"/tests/func/{CASE}/test01.jpg"
    browser.find_element_by_id('image_to_upload').send_keys(path)
    time.sleep(1000)

    """ Click to add a version. """
    browser.find_element_by_id('edit').click()
    add_version = browser.find_element_by_id('add_version')
    add_version.click()
    version_number = browser.find_element_by_name('newVersion[0].version_number')
    version_number.send_keys('TEST-01lp')
    upc = browser.find_element_by_name('newVersion[0].upc')
    upc.send_keys('123456')
    format = browser.find_element_by_name('newVersion[0].format')
    format.send_keys('LP')
    version_name = browser.find_element_by_name('newVersion[0].version_name')
    version_name.send_keys('Limited Edition Vinyl')

    """ Adds another version """
    browser.find_element_by_id('add_version').click()

    version_number = browser.find_element_by_name('newVersion[1].version_number')
    version_number.send_keys('TEST-01cd')
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
    assert version_number.get_attribute("value") == 'TEST-01cd'

    """ User goes to edit versions """
    browser.find_element_by_id('edit').click()

    upc = browser.find_element_by_name('version[0].upc')
    version_number = browser.find_element_by_name('version[0].version_number')
    version_name = browser.find_element_by_name('version[0].version_name')
    format = browser.find_element_by_name('version[0].format')

    upc.clear()
    upc.send_keys('11111')
    version_number.clear()
    version_number.send_keys('TEST-01cass')
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
    select.select_by_visible_text('Fishstick')

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
    select.select_by_visible_text('Fishstick')

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

    

    

