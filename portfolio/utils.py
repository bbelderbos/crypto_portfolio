from collections import namedtuple
from datetime import datetime
from io import StringIO

from bs4 import BeautifulSoup as Soup
import requests
from pycoingecko import CoinGeckoAPI
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image 
import matplotlib.ticker as mtick


URL = 'https://coingecko.com/en'
TOP_COINS = 25
Coin = namedtuple('Coin', 'rank logo name price market_cap volume change percent_change')

plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['text.color'] = 'white'
plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'

def scrape_coin_logos():
    html = requests.get(URL).text
    soup = Soup(html, 'lxml')
    return [tag.img['data-src'] for tag in soup.find_all
            ('div', class_='coin-icon mr-2 center flex-column')][:25]


def format_money(item):
    return '$' + '{:,}'.format(item)


def convert_unix_to_date(timestamp):
    return str(datetime.fromtimestamp(timestamp))


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


def chart_data(coin, currency='usd', days=1):
    cg = CoinGeckoAPI()
    chart = cg.get_coin_market_chart_by_id(coin, currency, days).get('prices')
    imgdata = StringIO()
    prices = {}

    for time, price in chart:
        time = int(str(time)[0:10])
        time = convert_unix_to_date(time).split()[1]
        prices[time] = round(price, 2)

    df = pd.DataFrame.from_dict({k:v for k, v in prices.items()}, orient='index', columns=['Price'])
    plot = df['Price'].plot(label=f'{coin.title()} Price in USD', figsize=(8,6), title=f'{coin.title()} Chart for Past 24 Hours')
    fmt = '${x:,.0f}'
    ticker = mtick.StrMethodFormatter(fmt)
    plot.yaxis.set_major_formatter(ticker)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    plt.cla()
    return data
    
    
    