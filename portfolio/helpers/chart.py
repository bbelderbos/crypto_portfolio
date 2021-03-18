from datetime import datetime
from io import StringIO

from pycoingecko import CoinGeckoAPI
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image 
import matplotlib.ticker as mtick


cg = CoinGeckoAPI()

plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['text.color'] = 'white'
plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'

def convert_unix_to_date(timestamp):
    return str(datetime.fromtimestamp(timestamp))


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