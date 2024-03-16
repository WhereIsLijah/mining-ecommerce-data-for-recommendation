from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

driver = webdriver.Chrome()

 
def scroller(url):
    driver.get(url)
    num_scrolls = 1
    

    while True:
        print(f"Number of scrolls: {num_scrolls}")
        elements = driver.find_elements("xpath", "//li[@class='UnWQ5']/div/div[@class='jWBBzf']/div[@class='kCClje']/h1")
        driver.execute_script("return arguments[0].scrollIntoView();", elements[-1])
        time.sleep(1)

        try:
            end_condition = driver.find_element("xpath", "//p[@class='lY5zDd']")
            print(end_condition.get_attribute("innerHTML"))
            break
        except NoSuchElementException:
            num_scrolls += 1

def extract_metadata_from_dataset(driver, dataset):
    """Extract metadata from a single dataset."""
    while True:
        try:
            # Click on the dataset to open the details pane
            dataset.click()

            # Wait for the details pane to become visible and extract the required details
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'zPqhQb')))

            title = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[3]/div/c-wiz[2]/c-wiz/div/div/div[1]/h1[1]/span'))
            ).text

            try:
                url = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[3]/div/c-wiz[2]/c-wiz/div/div/div[1]/div[1]/ul/li/c-wiz/div/div/a'))
                ).get_attribute('href')
            except:
                url = "URL not found"

            description_element = driver.find_element(By.CLASS_NAME, "iH9v7b")
            description_text = description_element.get_attribute("innerHTML")
            soup = BeautifulSoup(description_text, "html.parser")

            desc_clean = soup.get_text().replace('\n', '')

            metadata = {
                "title": title,
                "url": url,
                "description": desc_clean,
            }

            # Go back to the results page to proceed to the next dataset
            # driver.back()

            return metadata
        except StaleElementReferenceException:
            # If element reference becomes stale, try again
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle other exceptions as needed
            return None  # Or raise an exception

def extract_all_datasets_metadata(driver):
    """Navigate to the URL and extract metadata for the first 20 datasets listed."""
    time.sleep(5)  # Allow time for the initial content to load

    all_metadata = []
    try:
        # Find all <li> elements containing datasets
        li_elements = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[3]/div/c-wiz[1]/div/ol/li')

        #loop over all datasets
        for index, li_element in enumerate(li_elements[:-1]):
            print(f"Processing dataset {index + 1}...")
            # Extract metadata for the current dataset
            metadata = extract_metadata_from_dataset(driver, li_element)
            all_metadata.append(metadata)
            time.sleep(2)  # Add a small delay to avoid being too aggressive in your requests

    except Exception as e:
        print(f"An error occurred: {e}")

    return all_metadata


def main():
    try:
        url = "https://datasetsearch.research.google.com/search?src=3&query=e%20commerce&docid=L2cvMTF0ZGJxZzh2eg%3D%3D"
        scroller(url)
        all_metadata = extract_all_datasets_metadata(driver)
        with open("metadata.txt", "w") as file:
            for metadata in all_metadata:
                file.write(str(metadata)+ "\n")
                file.write("---------------\n")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
