import random
import re
import requests
import time

from bs4 import BeautifulSoup


class Store:
    def __init__(self, store_name: str, url: str, model: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/103.0.0.0 Safari/537.36 "
        }
        self.store = store_name
        self.model = model.upper()

    def morele(self):
        def _format(products):
            for product in products:
                name = product['data-product-name']
                lhr = " lhr" in name
                memory_gb = int([feature for feature in product.find_all("div", {"class": "cat-product-feature"}) if "ilość pamięci ram" in feature.text.lower()][0]['title'].lower().replace("gb", ""))
                if not product.find("a", href=re.compile(fr"/basket/add/{product['data-product-id']}")):
                    price = None
                    available = False
                else:
                    price = float(product['data-product-price'])
                    available = True
                new_url = "https://morele.net" + product.find("a", {"class": "productLink"})['href']
                brand = product['data-product-brand']
                print(self.model, price, brand, memory_gb, lhr)

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

    def run(self):
        match self.store:
            case "morele":
                self.morele()


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
