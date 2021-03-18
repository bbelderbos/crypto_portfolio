from bs4 import BeautifulSoup as Soup
import requests

URL = 'https://coingecko.com/en'
TOP_COINS = 25


def scrape_coin_logos():
    html = requests.get(URL).text
    soup = Soup(html, 'lxml')
    return [tag.img['data-src'] for tag in soup.find_all
            ('div', class_='coin-icon mr-2 center flex-column')][:TOP_COINS]