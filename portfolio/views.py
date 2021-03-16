from collections import namedtuple
from io import StringIO

from datetime import datetime, date, timedelta
from dateutil.parser import parse
from django.shortcuts import render
from pycoingecko import CoinGeckoAPI
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup as Soup
import requests

from portfolio.utils import get_coin_data, chart_data


def homepage(request):
    top_coins = get_coin_data()
    return render(request, 'home.html', {'top_coins': top_coins})


@csrf_exempt
def searchpage(request):
    if request.method == 'POST':
        coin = request.POST['coin'].lower()
        chart = chart_data(coin)
        return render(request, 'search.html', {'chart': chart})
    return render(request, 'search.html')
