import time

def login(browser):
    """ User goes to landing page """ 
    browser.get('http://localhost:3000/')

    """ User sees button for login, and clicks """
    browser.find_element_by_id('login').click()
    time.sleep(1)
    
    """ User submits username and password """
    email = browser.find_element_by_id('email')
    password = browser.find_element_by_id('password')
    submit = browser.find_element_by_id('submit')

    email.send_keys('admin@admin.com')
    password.send_keys('password')

    submit.click()
    time.sleep(3)
