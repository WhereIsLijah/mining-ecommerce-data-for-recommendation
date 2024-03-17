from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def initialize_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_kaggle_e_commerce_datasets(driver, start_url):
    driver.get(start_url)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "site-content")))
    dataset_metadata_list = []

    # Collect all dataset links on the current page
    dataset_links = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, "a[href*='/datasets/']")]

    # Iterate through each dataset link to collect metadata
    for link in dataset_links:
        driver.get(link)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "site-content")))

        # Extract the metadata
        try:
            title = driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div[2]/div/div[2]/div[2]')
            title_text = title.get_attribute("innerHTML")
            soup = BeautifulSoup(title_text, "html.parser")
            title_data = soup.get_text().replace('\n', '')
        except:
            title = "Title not found"
        
        try:
            description = driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div[2]/div/div[5]/div[1]/div[1]/div[2]')
            description_text = description.get_attribute("innerHTML")
            soup = BeautifulSoup(description_text, "html.parser")
            desc = soup.get_text().replace('\n', '')
        except:
            description = "Description not found"
        
        metadata = {
            "title": title_data,
            "url": link,
            "description": desc,
        }
        dataset_metadata_list.append(metadata)

        # Go back to the list of datasets
        driver.back()

    return dataset_metadata_list

def main():
    driver = initialize_driver()
    start_url = "https://www.kaggle.com/search?q=e-commerce+in%3Adatasets"
    metadata = scrape_kaggle_e_commerce_datasets(driver, start_url)
    
    with open("kaggle.txt", "w") as file:
        for data in metadata:
            file.write(str(data)+ "\n")
            file.write("---------------\n")
    driver.quit()

if __name__ == "__main__":
    main()
