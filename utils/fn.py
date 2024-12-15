import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def display_welcome_message():
    print("*" * 67)
    print("*" + " " * 19 + "Welcome to the SAFER Scraper!" + " " * 17 + "*")
    print("*" + " " * 8 + "This tool helps you scrape dispatcher information" + " " * 8 + "*")
    print("*" + " " * 12 + "from SAFER. Please follow the prompts below." + " " * 9 + "*")
    print("*" * 67)
    print("\n")

def is_valid_5_digit_number(input_value):
    # Check if input is a digit and exactly 5 characters long
    return input_value.isdigit() and len(input_value) == 5

def is_valid_2_digit_number(input_value):
    # Check if input is a digit and exactly 5 characters long
    return input_value.isdigit() and len(input_value) == 2

def clear_screen():
    os.system('cls')  # Command for Windows

def resource_path(relative_path):
    """Get the absolute path to a resource, works for both development and PyInstaller builds."""
    if hasattr(sys, '_MEIPASS'):  # Check if running in PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_element_by_loc(driver, locator, type = "text", retry = 0):
    try:
        wait = WebDriverWait(driver, 10)
        if type == "click":
            wait.until(EC.element_to_be_clickable((By.XPATH, locator)))
            driver.find_element(By.XPATH, locator).click()
        elif type == "element":
            wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
            return driver.find_element(By.XPATH, locator)
        elif type == "css":
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, locator)))
            temp = driver.find_element(By.CSS_SELECTOR, locator).text
            if temp == '':
                raise NotImplementedError()
            return temp
        else:
            wait.until(EC.presence_of_element_located((By.XPATH, locator)))
            temp = driver.find_element(By.XPATH, locator).text        
            if temp == '':
                raise NotImplementedError()
            return temp

    except Exception as e:
        if type == 'exists':
            return False
            
        if retry <= 1:
            print('\nLocator not found. Retrying...{}'.format(retry+1), end = '')
            driver.refresh()
            return get_element_by_loc(driver, locator, type, retry+1)
        else:
            print('\nSkipped.')
            return '—'