from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pytest
import json

import time

from royaltyapp.models import Artist, add_admin_user

from helpers import login

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
    time.sleep(10000)

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

    """ User clicks on artist detail and goes to artist page """
    artist_detail = browser.find_element_by_id('view-1')
    artist_detail.click()

    assert browser.find_element_by_id('prenom')
    heading = browser.find_element_by_id('header')
    assert heading.text == 'Artist Detail'
    assert browser.find_element_by_id('artist_name').get_attribute("value") == 'Fishstick'
    assert browser.find_element_by_id('prenom').get_attribute("value") == 'Bob'
    assert browser.find_element_by_id('surnom').get_attribute("value") == 'Nono'

    """ User can now see that contact was added. """
    assert browser.find_element_by_id('contact_prenom').get_attribute("value") == 'Bob'
    assert browser.find_element_by_id('contact_middle').get_attribute("value") == 'Bo'
    assert browser.find_element_by_id('contact_surnom').get_attribute("value") == 'Nono'

    """ User realizes they made mistake in the name, and updates spelling"""
    browser.find_element_by_id('edit').click()

    surnom = browser.find_element_by_id('surnom')
    surnom.clear()
    surnom.send_keys('Jones')

    contact_surnom = browser.find_element_by_id('contact_surnom')
    contact_surnom.clear()
    contact_surnom.send_keys('Jones')
    
    submit = browser.find_element_by_id('submit')
    submit.click()

    """ User navigates to view artist page """
    artist = browser.find_element_by_id('artists')
    artist.click()
    
    artist_detail = browser.find_element_by_id('view-1')
    artist_detail.click()
    assert browser.find_element_by_id('surnom').get_attribute("value") == 'Jones'
    assert browser.find_element_by_id('contact_surnom').get_attribute("value") == 'Jones'

    """ User adds another artist. """
    artist = browser.find_element_by_id('artists')
    artist.click()
    add_artist = browser.find_element_by_id('add_artist')
    add_artist.click()
    time.sleep(1)

    """ User arrives at new page to add artist """
    artist_name = browser.find_element_by_id('artist_name')
    prenom = browser.find_element_by_id('prenom')
    surnom = browser.find_element_by_id('surnom')
    submit = browser.find_element_by_id('submit')

    artist_name.send_keys('SpeakerBass')
    prenom.send_keys('Jo')
    surnom.send_keys('Jimi')

    submit.click()

    """ User can now see that artist was added. """
    table = browser.find_element_by_id('artist-table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(db.session.query(Artist).all()) == 2
    artist_detail = browser.find_element_by_id('view-2')
    artist_detail.click()

    time.sleep(10000)


    # """ User returns to main page and verifies change."""
    # table = browser.find_element_by_id('artist-table')
    # rows = table.find_elements_by_tag_name('tr')
    # tds = rows[1].find_elements_by_tag_name('td');
    # assert tds[2].text == 'Jones'

