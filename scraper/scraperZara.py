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
            todo = []

            elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zds-carousel-item")))
            element = elements[0]  
            soup_ul = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')

            list_items = soup_ul.find_all('li', class_='layout-categories-category layout-categories-category--level-2', attrs={'data-layout': 'products-category-view'})
            # print(list_items)
            for item in list_items:
                item = item.find('a')
                if item:
                    item_name = item.text.strip()
                    item_url = item['href']
                    categories.append({ "name": item_name, "url": item_url })

                result = self.scrape_and_save_products(item_url, item_name)
                todo.append(result)

            with open(self.output_file_path, 'w', encoding='utf-8') as output_file:
                jsonData = { "categories": categories }
                json.dump(jsonData, output_file, indent=4)

        except TimeoutException:
            print("Await time exceeded.")        

        finally:
            self.driver.quit()

    def scrape_and_save_products(self, parsed_url, parsed_name):
        driver = self.driver
        original_window = self.driver.current_window_handle
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])

        categories = []
        c_set = []


        driver.get(parsed_url)

        try:
            elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".view-option-selector-button")))
            time.sleep(1)
            if len(elements) > 2:
                elements[2].click()
            else:
                elements[1].click()

            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break

                last_height = new_height

            print("Scrolling Finished.")

            items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-grid-product")))
            print(parsed_name, len(items))
            i = 1
            for item in items:
                soup = BeautifulSoup(item.get_attribute('outerHTML'), 'html.parser')
                if soup.find(class_='money-amount__main') is None or soup.find(class_='product-link _item product-grid-product-info__name link') is None:
                    try:
                        url = soup.find(class_='product-link product-grid-product__link link')
                    except TimeoutException:
                        url = None
                    if url:
                        url = url['href']
                        name, price, product, c_set = self.scrape_specific(url, 2)
                    else:
                        name = price = url
                else:
                    name = soup.find(class_='product-link _item product-grid-product-info__name link').text.strip()
                    url = soup.find(class_='product-link product-grid-product__link link')['href']
                    price = soup.find(class_='money-amount__main').text.strip()

                    product = { "name": name, "url": url, "price": price }

                if c_set:
                    for item in c_set:
                        if item['name'] and item['url'] and item['price']:
                            print("Item -> ", i, " / ", len(items), " -> ", item['name'], item['url'], item['price'])
                            i = i + 1
                            categories.append(item)
                elif name and url and price and product:
                    print("Item -> ", i, " / ", len(items), " -> ", name, url, price)
                    i = i + 1
                    categories.append(product)

                c_set = []

        except TimeoutException:
            print("Await time exceeded.")    

        driver.close()
        driver.switch_to.window(original_window)

        return {"name": parsed_name, "url": parsed_url, "products": categories}
    
    def scrape_specific(self, url, window_number):
        driver = self.driver
        original_window = self.driver.current_window_handle
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[window_number])

        c_set = []
        driver.get(url)

        try:
            clothing_set = WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".carousel__item")))
        except TimeoutException:
            clothing_set = None

        if not clothing_set:
            try:
                elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-detail-info__header-name")))
                money = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".money-amount__main")))
                name = elements[0].text.strip()
                price = money[0].text.strip()  

                product = { "name": name, "url": url, "price": price }
                c_set = None
            except TimeoutException:
                print("Await time exceeded.")

        else:
            for cloth in clothing_set:
                soup = BeautifulSoup(cloth.get_attribute('outerHTML'), "html.parser")
                url_cloth = soup.find('a').get('href')
                name_cloth, price_cloth, x, y = self.scrape_specific(url_cloth, 3)

                if name_cloth and url_cloth and price_cloth:
                    c_set.append({ "name": name_cloth, "url": url_cloth, "price": price_cloth })
                
            name = price = product = None
        driver.close()
        driver.switch_to.window(original_window)   


        return name, price, product, c_set
