from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import json, re, time

class ZaraProductsScraper:
    def __init__(self, url, output_file_path):
        self.url = url
        self.output_file_path = output_file_path
        self.driver = webdriver.Chrome()

    def scrape_and_save_categories(self):
        self.driver.get(self.url)

        try:
            reject_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
            reject_button.click()
        except TimeoutException:
            print("Cookies button not found.")

        try:
            menu_item = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "layout-header-icon")))
            menu_item.click()
            categories = []

            elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zds-carousel-item")))
            element = elements[0]  
            soup_ul = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')

            list_items = soup_ul.find_all('li', class_='layout-categories-category layout-categories-category--level-2', attrs={'data-layout': 'products-category-view'})
            # print(list_items)
            for item in list_items:
                item = item.find('a')
                if item:
                    categories.append({ "name": item.text.strip(), "url": item['href'] })
                    print("NAME -> ", item.text.strip(), "\nURL -> ", item['href'])

            with open(self.output_file_path, 'w', encoding='utf-8') as output_file:
                jsonData = { "categories": categories }
                json.dump(jsonData, output_file, indent=4)

        except TimeoutException:
            print("Await time exceeded.")        


