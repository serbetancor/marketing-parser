from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json, time

class MangoProductsScraper:
    def __init__(self, url, output_file_path):
        self.url = url
        self.output_file_path = output_file_path
        self.driver = webdriver.Chrome()

    def scrape_and_save_categories(self):
        self.driver.get(self.url)


        try:
            reject_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="cookies.button.rejectAll"]')))   
            reject_button.click()
        except TimeoutException:
            print("Cookies button not found.")

        try:
            menu_women = self.driver.find_element(By.ID, "sheMenu")
            action_chains = ActionChains(self.driver)
            action_chains.move_to_element(menu_women).perform()

            time.sleep(2)

            categories = []

            ul_element = self.driver.find_element(By.ID, "subMenuColumn2")
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li:not(:first-child)")
            for li_element in li_elements:
                a_element = li_element.find_element(By.TAG_NAME, "a")

                item_url = a_element.get_attribute("href")
                item_name = a_element.text

                result = self.scrape_and_save_products(item_url, item_name)
                categories.append(result)

            with open(self.output_file_path, 'w', encoding='utf-8') as output_file:
                jsonData = { "categories": categories }
                json.dump(jsonData, output_file, indent=4)


            print("Done")
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
        driver.get(parsed_url)

        try:
            time.sleep(2)
            while True:
                current_height = driver.execute_script("return window.scrollY + window.innerHeight;")
                driver.execute_script("window.scrollTo(0, Math.min(document.body.scrollHeight, window.scrollY + 700));")
                time.sleep(0.5)
                if current_height >= driver.execute_script("return document.body.scrollHeight;"):
                    break

            products = []
            
            div_element = driver.find_element(By.ID, "catalogProductsList")
            ul_element = div_element.find_element(By.CSS_SELECTOR, "ul.EbO8r[data-testid='plp.grid.4']")
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li.w5Xes.WG13V")

            i = 0

            for li_element in li_elements:
                soup = BeautifulSoup(li_element.get_attribute('outerHTML'), 'html.parser')

                name = url = ""
                price = "0.00"
                colours = 0

                if soup.find(class_='layout-row md12 text-body-m') and soup.find(class_='H2rhU') and (soup.find(class_='PeSJ4 text-body-m') or soup.find(class_='PeSJ4 text-body-m GsPZp')):
                    name = soup.find(class_='layout-row md12 text-body-m').text.strip()
                    url = parsed_url + soup.find(class_='H2rhU')['href']
                    if soup.find(class_='PeSJ4 text-body-m'):
                        price = soup.find(class_='PeSJ4 text-body-m').text.strip().replace(",", ".").replace(" €", "")
                    else:
                        price = soup.find(class_='PeSJ4 text-body-m GsPZp').text.strip().replace(",", ".").replace(" €", "")

                    if soup.find(class_='layout-row tntot'):
                        colours = len(soup.find(class_='layout-row tntot').find_all('button'))
                    else:
                        colours = 1

                product = {
                    "name": name,
                    "url": url,
                    "price": price,
                    "variety": colours
                }
                if name == "":
                    print(i, "->", product)

                products.append(product)
                i=i+1

            print(len(li_elements))

        except TimeoutException:
            print("Await time exceeded.")    

        driver.close()
        driver.switch_to.window(original_window)

        return {"name": parsed_name, "url": parsed_url, "products": products}