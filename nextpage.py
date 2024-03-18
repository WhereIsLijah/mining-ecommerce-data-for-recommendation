from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def initialize_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def navigate_pages(driver, start_url, css_selector_for_next_button):
    driver.get(start_url)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "site-content")))
    
    page = 1
    while True:
        print(f"Page: {page}")
        try:
            next_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector_for_next_button))
            )
            # Use ActionChains if you need to scroll to the element before clicking
            ActionChains(driver).move_to_element(next_page_button).click().perform()
            page += 1
            time.sleep(5)  # Wait for the page to load. Adjust as needed.
        except Exception as e:
            print(f"Finished navigating pages. Last page: {page}. Error: {str(e)}")
            break

def main():
    driver = initialize_driver()
    try:
        start_url = "https://www.kaggle.com/search?q=e-commerce+in%3Adatasets"
        css_selector_for_next_button = "#results > div.sc-hXOTHz.hNNTl > i:nth-child(12)"  # Adjust the selector if needed
        navigate_pages(driver, start_url, css_selector_for_next_button)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
