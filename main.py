from utils.loc import locators
from utils.fn import get_element_by_loc, clear_screen, resource_path, is_valid_2_digit_number, is_valid_5_digit_number, display_welcome_message
from datetime import datetime
import time
import re
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm  # Import tqdm for progress bar

base_url = 'https://safer.fmcsa.dot.gov/CompanySnapshot.aspx'

def init_driver():
    clear_screen()

    print('Initializing..........')
    print('\n')

    # Set up the WebDriver
    opera_driver_path = resource_path("driver/operadriver.exe")
    opera_binary_path = resource_path("opera/opera.exe")
    opera_profile = resource_path("profile")
    
    webdriver_service = Service(opera_driver_path)
    webdriver_service.start()

    options = webdriver.ChromeOptions()
    options.binary_location = opera_binary_path
    
    # Configure the Opera profile and user agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0'
    options.add_argument(f'user-data-dir={opera_profile}')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-extensions')
    options.add_experimental_option('w3c', True)

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(service=webdriver_service, options=options)

    time.sleep(5)
    print('Initialization Completed.')
    return driver

def scrape(driver, base_url, start_number, itr):
    mx_numbers = list(range(start_number, start_number + itr))

    df = pd.DataFrame(columns=['MX_NUMBER', 'Status', 'Power Unit', 'Drivers', 'Phone'])

    now = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

    clear_screen()
    
    for mx_num in tqdm(mx_numbers, desc="Scraping Progress", ncols=100):
        print('\n\nJob Started At: {}'.format(now))
        print("Current Job: {}".format(mx_num))

        if not is_valid_5_digit_number(str(mx_num)):
            print('Status: Skipped')
            continue

        driver.get(base_url)

        get_element_by_loc(driver, locators['SELECT_MX_RADIO'], 'click')
        
        search = get_element_by_loc(driver, locators['INPUT_MX_NUMBER'], 'element')

        search.send_keys(mx_num)

        search.submit()

        time.sleep(3)

        record_not_found = get_element_by_loc(driver, locators['NOT_FOUND'], 'exists')

        if not record_not_found:

            entity_type = get_element_by_loc(driver, locators['ENTITY_TYPE'], 'element')

            if(entity_type.text.strip() != 'CARRIER'):
                print('Status: Entity is not Carrier.')
                continue

            status = get_element_by_loc(driver, locators['USDOT_STATUS'], 'element')

            power_unit = get_element_by_loc(driver, locators['POWER_UNIT'], 'element')

            driver_count = get_element_by_loc(driver, locators['DRIVERS'], 'element')
            
            phone = get_element_by_loc(driver, locators['PHONE'], 'element')

            df.loc[len(df.index)] = [mx_num, status.text, power_unit.text, driver_count.text, phone.text]
            print('Status: Completed')
        else:
            print('Status: Not Found')

        clear_screen()

    df.to_csv("{}.xlsx".format(now), index=False)

if __name__ == '__main__':
    try:
        display_welcome_message()
        
        mx_number_valid = False
        itr_valid = False

        while(not mx_number_valid):
            try:
                start_number = input('Please enter starting MX Number: ')
            
                # Validation
                if not is_valid_5_digit_number(start_number):
                    raise ValueError("Invalid input. Please enter a 5-digit number. For Example 32234")
                else:
                    mx_number_valid = True
            except Exception as e:
                print(e)

        while(not itr_valid):
            try:
                itr = input('How much mx numbers do you want to iterate ? (10 - 99). ')

                # Validation
                if not is_valid_2_digit_number(itr):
                    raise ValueError("Invalid input. Please enter number b/w 10 - 99. For Example 51")
                else:
                    itr_valid = True
            except Exception as e:
                print(e)

        driver = init_driver()

        scrape(driver, base_url, int(start_number), int(itr))
                
        driver.close()
        driver.quit()

        input("\nScrapping Completed! Press ENTER key to quit...")

    except (KeyboardInterrupt, EOFError):
        print('\nExit.')
    except Exception as e:
        print(e)