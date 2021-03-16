from collections import namedtuple
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from django.shortcuts import render
from pycoingecko import CoinGeckoAPI
from django.contrib.auth.models import User

from bs4 import BeautifulSoup as Soup
import requests

from portfolio.utils import scrape_coin_logos, format_money, get_coin_data


def homepage(request):
    top_coins = get_coin_data()
    return render(request, 'home.html', {'top_coins': top_coins})
