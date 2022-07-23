import requests

from bs4 import BeautifulSoup


def olx_search(search_phrase: str) -> dict:
    # TODO: Take dict with all info about card (brand, memory etc.) as an argument, then parse it to search phrase
    search_phrase = search_phrase.replace(" ", "-")

    url = f"https://www.olx.pl/d/elektronika/komputery/podzespoly-i-czesci/karty-graficzne/q-{search_phrase}/"
    response = requests.get(url, headers={})
    soup = BeautifulSoup(response.text, 'lxml')

    pagination = soup.find("div", {"data-testid": "pagination-wrapper"})
    if not pagination:
        pages = 1
    else:
        # TODO: Catch Exceptions
        pages = int(pagination.find_all("li", {"data-testid": "pagination-list-item"})[-1].a.text)

    offers = soup.find("div", {"data-testid": "listing-grid"}).find_all("div", recursive=False)

    for offer in offers:
        name = offer.find("h6")
        if not name:
            continue
        # TODO: Check and compare information between arg dict and name


if __name__ == "__main__":
    olx_search("karta graficzna")
