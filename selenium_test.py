from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def select_first_suggestion(location):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get('https://weather.com') #url for scraping
        wait = WebDriverWait(driver, 5)
        search_box = wait.until(EC.element_to_be_clickable((By.ID, 'LocationSearch_input')))
        
        search_box.send_keys(location)
        # Wait for the dropdown to ensure suggestions are loaded
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="WxuHeaderLargeScreen-header-9944ec87-e4d4-4f18-b23e-ce4a3fd8a3ba"]/header/div/div[2]/div[1]/form/div/div[2]')))
        
        time.sleep(2)  
        search_box.send_keys(Keys.DOWN + Keys.RETURN)  # Navigate to the first suggestion
        time.sleep(1) #wait for page to load

        # Wait for the page to update with the selected location's weather
        degrees = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="WxuSavedLocations-header-9aea3e61-fbf8-4da4-9e07-f96abf18cdf1"]/div/div/div/div[1]/div[1]/div/div[1]/a[1]/span')))
        full_location = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="WxuSavedLocations-header-9aea3e61-fbf8-4da4-9e07-f96abf18cdf1"]/div/div/div/div[1]/div[1]/div/div[1]/a[2]/span[1]')))


        print(f'Current temperature in {full_location.text}: {degrees.text}')
    
    finally:
        driver.quit()

weather = input("Enter the location of choice:").strip()
select_first_suggestion(weather)
