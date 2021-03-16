from bs4 import BeautifulSoup as Soup
import requests
from collections import namedtuple
from pycoingecko import CoinGeckoAPI


URL = 'https://coingecko.com/en'
TOP_COINS = 25
Coin = namedtuple('Coin', 'rank logo name price market_cap volume change percent_change')

def scrape_coin_logos():
    html = requests.get(URL).text
    soup = Soup(html, 'lxml')
    return [tag.img['data-src'] for tag in soup.find_all
            ('div', class_='coin-icon mr-2 center flex-column')][:25]


def format_money(item):
    return '$' + '{:,}'.format(item)


def get_coin_data():
    coin_data = CoinGeckoAPI()
    top_coins = []
    logos = scrape_coin_logos()

    for idx, item in enumerate(coin_data.get_coins_markets('usd')[:TOP_COINS]):
        coin = Coin(rank=idx+1, logo=logos[idx], name=item['id'].title(), price=format_money(item['current_price']),
                market_cap=format_money(item['market_cap']), volume=format_money(item['total_volume']),
                change=format_money(item['price_change_24h']), percent_change=item['price_change_percentage_24h'])
        top_coins.append(coin)
    return top_coins