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
            ('div', class_='coin-icon mr-2 center flex-column')][:TOP_COINS]


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


def single_coin_data(coin):
    cg = CoinGeckoAPI()
    SingleCoin = namedtuple('SingleCoin', 'id symbol link1 link2 image market_cap_rank ath price mcap volume')
    data = cg.get_coin_by_id(coin.lower())
    id = data['id'].title()
    symbol = data['symbol'].upper()
    link1 = data['links']['homepage'][0]
    link2 = data['links']['blockchain_site'][0]
    image = data['image']['small']
    market_cap_rank = data['market_cap_rank']
    price_data = cg.get_coins_markets('usd')[market_cap_rank-1]
    ath = '$' + str(data['market_data']['ath']['usd'])
    price = format_money(price_data['current_price'])
    mcap = format_money(price_data['market_cap'])
    volume = format_money(price_data['total_volume'])
    return SingleCoin(id=id, symbol=symbol, link1=link1, link2=link2, image=image,
                      market_cap_rank=market_cap_rank, ath=ath, price=price, mcap=mcap, volume=volume)


def single_coin_exchanges(coin):
    cg = CoinGeckoAPI()
    exchange_info = []
    Exchanges = namedtuple('Exchanges', 'name volume')
    data = cg.get_coin_by_id(coin.lower())['tickers']
    names = [name['market']['name'] for name in data if name['target'] == 'USDT']
    volumes = [round(vol['volume'], 2) for vol in data if vol['target'] == 'USDT']
    for i in range(5):
        exchange = Exchanges(name=names[i], volume=format_money(volumes[i]))
        exchange_info.append(exchange)
    return exchange_info


def chart_data(coin, currency='usd', days=1):
    cg = CoinGeckoAPI()
    chart = cg.get_coin_market_chart_by_id(coin, currency, days).get('prices')
    imgdata = StringIO()
    prices = {}

    for time, price in chart:
        time = int(str(time)[0:10])
        time = convert_unix_to_date(time).split()[1]
        prices[time] = round(price, 2)
        print(prices[time])

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
    
    
    