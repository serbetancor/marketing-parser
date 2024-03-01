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
            print("El botón para rechazar las cookies no se encontró o no se pudo hacer clic en él.")

        try:
            menu_item = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "layout-header-icon")))
            menu_item.click()

            elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zds-carousel-item")))
            for element in elements:
                soup_ul = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')

                lista_items = soup_ul.find_all('li', class_='layout-categories-category', attrs={'data-layout': 'products-category-view'})
                # print(lista_items)
                for item in lista_items:
                    print(item.text)

        except TimeoutException:
            print("Tiempo de espera excedido mientras se esperaban los elementos para cargar.")

        print("Hi")
        


