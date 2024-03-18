from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import psycopg2
from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename} file.')
    return db

def connect_db():
    params = config()
    conn = psycopg2.connect(**params)
    return conn

def insert_metadata(conn, metadata):
    try:
        cur = conn.cursor()
        insert_query = "INSERT INTO ecommerce_metadata.metadata (id, title, url, description) VALUES (%s, %s, %s, %s);"
        for data in metadata:
            cur.execute(insert_query, (data['id'], data['title'], data['url'], data['description']))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def initialize_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scroll_and_click_next(driver, next_page_button_selector):
    next_page_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, next_page_button_selector))
    )
    # Scroll to the element
    ActionChains(driver).move_to_element(next_page_button).perform()
    # Now click
    next_page_button.click()

def scrape_kaggle_e_commerce_datasets(driver, start_url):
    driver.get(start_url)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "site-content")))
    dataset_metadata_list = []
    id = 0
    page = 1

    while True:
        # Collect all dataset links on the current page
        dataset_links = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, "a[href*='/datasets/']")]

        # Iterate through each dataset link to collect metadata
        for link in dataset_links:
            driver.get(link)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "site-content")))
            id += 1
            # Extract the metadata
            try:
                title_element = driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]')
                title_data = title_element.text
            except:
                title_data = "Title not found"

            try:
                description_element = driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div[2]/div/div[5]/div[1]/div[1]/div[2]')
                desc = description_element.text
            except:
                desc = "Description not found"

            metadata = {
                "id": id,
                "title": title_data,
                "url": link,
                "description": desc,
            }
            dataset_metadata_list.append(metadata)

            # Go back to the list of datasets
            driver.back()

        # Find and click the next page button, adjust the selector as needed
        next_page_button_selector = '//*[@id="results"]/div[2]/i[2]'  # Example XPath, update as needed
        try:
            scroll_and_click_next(driver, next_page_button_selector)
            time.sleep(5)  # Adjust timing as necessary for page loading
        except:
            print("No more pages or unable to locate next page button.")
            break

    return dataset_metadata_list

def main():
    driver = initialize_driver()
    start_url = "https://www.kaggle.com/search?q=e-commerce+in%3Adatasets"
    metadata = scrape_kaggle_e_commerce_datasets(driver, start_url)
    
    # Connect to the database
    conn = connect_db()
    # Insert metadata into the database
    insert_metadata(conn, metadata)
    print(f"Metadata for {len(metadata)} datasets extracted and inserted into the database.")
    
    # Write metadata to a text file
    with open("metadata.txt", "w") as f:
        for data in metadata:
            f.write(f"ID: {data['id']}\nTitle: {data['title']}\nURL: {data['url']}\nDescription: {data['description']}\n\n")
    
    print(f"Metadata for {len(metadata)} datasets also written to metadata.txt.")
    driver.quit()

if __name__ == "__main__":
    main()