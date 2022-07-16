import random
import re
import requests
import time
import urllib.parse

import selenium.webdriver.chrome.webdriver

from addons import brand_detector
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as Service

from webdriver_manager.chrome import ChromeDriverManager


class Store:
    def __init__(self, store_name: str, url: str, model: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/103.0.0.0 Safari/537.36 ",
        }
        self.store = store_name
        self.model = model.upper()

    def get_webdriver(self) -> webdriver.chrome.webdriver.WebDriver:
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        options.add_argument("--start-maximized")

        # That's for linux vm
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-sandbox")
        # display = Display(visible=0, size=(1366, 768))
        # display.start()

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    @staticmethod
    def webdriver_page_has_loaded(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> bool:
        return driver.execute_script('return document.readyState;') == 'complete'

    def morele(self):
        formatted = []

        def _format(products):
            for product in products:
                name = product['data-product-name']
                lhr = "lhr" in name.lower()
                memory_gb = int([feature for feature in product.find_all("div", {"class": "cat-product-feature"}) if "ilość pamięci ram" in feature.text.lower()][0]['title'].lower().replace("gb", ""))
                if not product.find("a", href=re.compile(fr"/basket/add/{product['data-product-id']}")):
                    price = None
                    available = False
                else:
                    price = float(product['data-product-price'])
                    available = True
                product_url = "https://morele.net" + product.find("a", {"class": "productLink"})['href']
                brand = product['data-product-brand']
                formatted.append({
                    "name": name,
                    "availability": available,
                    "price": price,
                    "url": product_url,
                    "lhr": lhr,
                    "memory": memory_gb,
                    "brand": brand
                })

        base_url = self.url
        headers = self.headers
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            pages = int(soup.find("ul", {"class": "pagination", "data-href": True})['data-count'])
        except IndexError:
            pages = 1

        _format(soup.find_all("div", {"class": "cat-product"}))

        if pages > 1:
            for page in range(2, pages + 1):
                time.sleep(random.uniform(0.5, 6.0))
                if base_url[-1] == '/':
                    url_with_page = f"{base_url}{page}"
                else:
                    url_with_page = f"{base_url}/{page}"
                response = requests.get(url_with_page, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')

                _format(soup.find_all("div", {"class": "cat-product"}))

        return formatted

    def mediaexpert(self):
        formatted = []

        def _format(products):
            for product in products:
                name_and_url = product.find_element(By.CLASS_NAME, 'spark-link')
                name = name_and_url.text
                lhr = "lhr" in name.lower()
                if len(re.findall(r"\d{1,2}GB", name)) > 0:
                    memory_gb = int(re.findall(r"\d{1,2}GB", name)[0].lower().replace("gb", ""))
                else:
                    memory_gb = int(int(product.find_element(By.XPATH, '//span[contains(text(), "Ilość pamięci RAM [MB]")]').find_element(By.XPATH, '../..').text.split(":")[1]) / 1024)

                try:
                    product.find_element(By.XPATH, '//button[contains(@class, "add-to-cart")]')
                    whole = product.find_element(By.CLASS_NAME, 'whole').text
                    rest = product.find_element(By.CLASS_NAME, 'cents').text
                    price = float(f"{whole.strip()}.{rest.strip()}".encode("ascii", "ignore").decode())
                    available = True
                except NoSuchElementException:
                    price = None
                    available = None

                product_url = name_and_url.get_attribute('href')
                brand = brand_detector(name)

                formatted.append({
                    "name": name,
                    "availability": available,
                    "price": price,
                    "url": product_url,
                    "lhr": lhr,
                    "memory": memory_gb,
                    "brand": brand
                })

        params = {"limit": 50}
        req = requests.models.PreparedRequest()
        req.prepare_url(self.url, params)
        url = req.url

        driver = self.get_webdriver()
        driver.get(url)
        while not self.webdriver_page_has_loaded(driver):
            time.sleep(0.1)
        _format(driver.find_elements(By.XPATH, '//div[@class="offers-list"]/span'))

        try:
            pages = int(driver.find_element(By.XPATH, '//span[@class="from"]').text.replace("z", ""))
        except NoSuchElementException:
            pages = 1

        if pages > 1:
            for page in range(2, pages + 1):
                time.sleep(random.uniform(0.5, 6.0))
                params["page"] = page
                req.prepare_url(self.url, params)
                url = req.url
                print(url)
                driver.get(url)
                while not self.webdriver_page_has_loaded(driver):
                    time.sleep(0.1)
                _format(driver.find_elements(By.XPATH, '//div[@class="offers-list"]/span'))

        driver.quit()

        return formatted

    def run(self):
        match self.store:
            # case "morele":
            #     self.morele()
            case "mediaexpert":
                self.mediaexpert()


if __name__ == "__main__":
    import json

    with open("urls_stores.json", "r") as urls_json:
        data = json.load(urls_json)

    amd_models = data['amd radeon']
    nvidia_models = data['nvidia geforce']

    for model in nvidia_models:
        model_urls = nvidia_models[model]
        for store in model_urls['urls']:
            _url = model_urls['urls'][store]
            if not _url:
                continue
            store_obj = Store(store, _url, model)
            store_obj.run()
