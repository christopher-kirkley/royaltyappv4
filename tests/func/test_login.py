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

def test_login_no_user(browser, test_client, db):
    """ User goes to landing page """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'

    """ User sees button for login, and clicks """
    browser.find_element_by_id('login').click()
    time.sleep(1)
    
    email = browser.find_element_by_id('email')
    password = browser.find_element_by_id('password')
    submit = browser.find_element_by_id('submit')
    time.sleep(1)

    email.send_keys('user@hotmail.com')
    password.send_keys('password')
    
    submit.click()

    alert = browser.find_element_by_id('alert')
    assert alert.text == 'Invalid Login'


def test_login_valid_user(browser, test_client, db):
    """ User goes to landing page """ 
    browser.get('http://localhost:3000/')
    assert browser.title == 'Royalty App'

    """ User sees button for login, and clicks """
    browser.find_element_by_id('login').click()
    time.sleep(1)
    
    """ User submits username and password """
    email = browser.find_element_by_id('email')
    password = browser.find_element_by_id('password')
    submit = browser.find_element_by_id('submit')
    time.sleep(1)

    email.send_keys('user@hotmail.com')
    password.send_keys('password')
    
    submit.click()

    """ Successful login redirects to dashboard """
    header = browser.find_element_by_id('header')
    assert header.text == 'Dashboard'
