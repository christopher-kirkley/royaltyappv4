from selenium import webdriver


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
    browser.get('http://localhost:5000')
    assert browser.title == 'Artists'
    
    """ User sees an empty list, clicks on button to add artist """
    add_artist = browser.find_element_by_id('add_artist')
    add_artist.click()
    time.sleep(1)

    """ User arrives at new page to add artist """
    assert browser.title == 'New Artist'

    """ User adds a new artist """
    artist_name = browser.find_element_by_id('artist_name')
    prenom = browser.find_element_by_id('prenom')
    surnom = browser.find_element_by_id('surnom')
    submit = browser.find_element_by_id('submit')

    artist_name.send_keys('Amanar')
    prenom.send_keys('Ahmed')
    surnom.send_keys('Ag Kaedi')
    submit.click()
    time.sleep(2)

    """ User returns to main artist page """
    assert browser.title == 'Artists'
    
    """ User can now see that artist was added. """
    table = browser.find_element_by_id('artist_table')
    rows = table.find_elements_by_tag_name('tr')
    assert len(db.session.query(Artist).all()) == 1
    tds = rows[1].find_elements_by_tag_name('td');
    assert tds[0].text == 'Amanar'
    assert tds[1].text == 'Ahmed'
    assert tds[2].text == 'Ag Kaedi'

    


    
    
