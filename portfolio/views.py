# from collections import namedtuple
# from io import StringIO

# from datetime import datetime, date, timedelta
# from dateutil.parser import parse
from django.shortcuts import render
# from pycoingecko import CoinGeckoAPI
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
# from bs4 import BeautifulSoup as Soup
# import requests

from portfolio.helpers.chart import chart_data
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.helpers.coin_data import CoinData

cg = CoinData()

def homepage(request):
    top_coins = cg.get_all_coin_data(scrape_coin_logos())
    return render(request, 'home.html', {'top_coins': top_coins})


@csrf_exempt
def searchpage(request):
    if request.method == 'POST':
        coin = request.POST['coin'].lower()
        chart = chart_data(coin)
        data = cg.single_coin_data(coin)
        exchanges = cg.single_coin_exchanges(coin)
        return render(request, 'search.html', {'chart': chart, 'data': data, 'exchanges': exchanges})
    return render(request, 'search.html')
