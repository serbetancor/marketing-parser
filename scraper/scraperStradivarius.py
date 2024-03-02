from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import json, re, time

class StradivariusProductsScraper:
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
            menu_item = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "clickable-area")))
            menu_item.click()

            elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".content-categories-desktop > * > * > *")))
            items_list = []
            flag = False

            for element in elements:
                if flag:    
                    item_url_category = None
                    subcategory_items = element.find_elements(By.CSS_SELECTOR, ".subcategory-item-3-level")
                    subcategory_list = []
                    sum = 0

                    for subcategory_item in subcategory_items:
                        sub = subcategory_item.find_element(By.CSS_SELECTOR, "a.item-subcategory")
                        subcategory_name = (re.search('>(.*?)<', sub.get_attribute('outerHTML'))).group(1)
                        subcategory_href = sub.get_attribute('href')

                        quantity, products = self.scrape_and_save_products(subcategory_href, subcategory_name)
                        sum += quantity
                        
                        section = {"name": subcategory_name, "url": subcategory_href, "quantity": quantity, "products": products}
                        subcategory_list.append(section)
                    
                    item_info = {"name": item_category, "url": item_url_category, "quantity": sum, "section": subcategory_list}
                    items_list.append(item_info)
                    sum = 0
                    flag = False
                else:
                    item_category = element.text.strip()
                    item_url_category = element.get_attribute('href')
                    if item_url_category == "javascript:void(0)":
                        flag = True
                    elif item_category and item_url_category:
                        quantity, products = self.scrape_and_save_products(item_url_category, item_category)
                        item_info = {"name": item_category, "url": item_url_category, "quantity": quantity ,"section": None, "products": products }
                        items_list.append(item_info)

            with open(self.output_file_path, 'w', encoding='utf-8') as output_file:
                jsonData = { "categories": items_list }
                json.dump(jsonData, output_file, indent=4)

            print(f"Data saved in {self.output_file_path}")

        except TimeoutException:
            print("Await time exceeded.")
        except ElementClickInterceptedException:
            print("Intercepted element.")

        finally:
            self.driver.quit()

    def scrape_and_save_products(self, url_section, parsed_name):
        driver = self.driver
        original_window = self.driver.current_window_handle
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        number = 0

        # url_section = "https://www.stradivarius.com/es/mujer/ropa/punto-n1976"

        dead_urls = ["https://www.stradivarius.com/es/gift-card.html", "https://www.stradivarius.com/es/nueva-colecci%C3%B3n/ropa/compra-por-producto/promociones-c1020096049.html", "https://www.stradivarius.com/es/mujer/zapatos/special-prices-n2515"]
        products = []
        driver.get(url_section)
        print("Trying to reach -> ", url_section)
        if url_section not in dead_urls:
            try:
                elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sc-beySPh")))
                for element in elements:
                    if "Vista" in element.get_attribute('outerHTML'):
                        element.click()
                        last_height = driver.execute_script("return document.body.scrollHeight")

                        while True:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(5)
                            new_height = driver.execute_script("return document.body.scrollHeight")
                            if new_height == last_height:
                                break

                            last_height = new_height

                        print("Scrolling Finished.")

                        items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-iJrEMN")))

                        for item in items:
                            soup = BeautifulSoup(item.get_attribute('outerHTML'), 'html.parser')

                            name = soup.find(class_='sc-beySPh dtUhOe').text.strip()
                            price = soup.find(class_='price').text.strip()

                            if "sc-jsEeTM hreQka" in str(soup):
                                url = soup.find(class_='sc-jsEeTM hreQka').a['href']
                            else:
                                print("NO ENCONTRADO")
                                url = soup.find(class_='sc-cxtRbA fUIUDg').a['href']

                                
                            product = { "name": name, "url": url, "price": float(re.sub(r'[^\d,.]', '', price).replace(',', '.')) }
                            products.append(product)

                        print("Getting products finished.")
                        
                        number = len(items)
                        print("Items captured for", parsed_name, "-> ", number, "\n")

                driver.close()
                driver.switch_to.window(original_window)
            except TimeoutException:
                print("Await time exceeded.")
        else:
            driver.close()
            driver.switch_to.window(original_window)
        
        return number, products


