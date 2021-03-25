from collections import namedtuple
from unittest.mock import Mock, patch
from typing import List, Sequence, Any

import pytest
from django.contrib.auth.models import User

from portfolio.helpers.coin_data import CoinData
from portfolio.helpers.chart import convert_unix_to_date, chart_data, portfolio_pie_chart
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.helpers.portfolio import Portfolio
from portfolio.models import PortfolioHoldings

Fields = namedtuple('Fields', 'ticker num_coins usd_amt coin_name type_')
cg = CoinData()


@pytest.mark.django_db(transaction=True)
def create_user_and_class_instance():
    user = User.objects.create_user(username='joe', password='tesTing123%')
    pt = Portfolio(user)
    return user, pt


@pytest.mark.parametrize('ticker, num_coins, usd_amt, coin_name, type_', [
    ('ICX', 26000.326, 52000.35, 'icon', 'Buy'),
    ('DOT', 300, 9000, 'DOT', 'Sell')
])


@pytest.mark.django_db(transaction=True)
def test_no_user_coins(ticker, num_coins, usd_amt, coin_name, type_):
    user = User.objects.create_user(username='joe', password='tesTing123%')
    pt = Portfolio(user)
    pt.no_user_coins(ticker, num_coins, usd_amt, coin_name, type_)
    query = PortfolioHoldings.objects.filter(person=user, coin_ticker=ticker).first()

    if ticker == 'ICX':
        assert query.coin_ticker == 'ICX'
    else:
        assert query is None


@pytest.mark.parametrize('ticker, num_coins, usd_amt, coin_name, type_', [
    ('ICX', 26000.326, 52000.35, 'icon', 'Buy'),
    ('DOT', 300, 9000, 'DOT', 'Sell')
])


@pytest.mark.django_db(transaction=True)
def test_delete_coin(ticker, num_coins, usd_amt, coin_name, type_):
    user = User.objects.create_user(username='joe', password='tesTing123%')
    pt = Portfolio(user)
    PortfolioHoldings.objects.create(coin_ticker=ticker, number_of_coins=num_coins,
                            amount_in_usd=usd_amt, coin_name=coin_name, type=type_,
                            person=user)
    query = PortfolioHoldings.objects.filter(person=user)
    fields = Fields(ticker=ticker, num_coins=num_coins, usd_amt=usd_amt,
                    coin_name=coin_name, type_=type_)
    pt.delete_coin(query, fields)
    assert query.filter(coin_ticker=ticker).first() is None


@pytest.mark.parametrize('ticker, coin_amt, usd_amt, coin_name, type_', [
    ('ICX', 26000.326, 52000.35, 'icon', 'Buy'),
    ('DOT', 300, 9000, 'DOT', 'Sell')
])


@pytest.mark.django_db(transaction=True)
def test_update_or_delete_coin(ticker, coin_amt, usd_amt, coin_name, type_):
    user, pt = create_user_and_class_instance()
    if ticker == 'ICX':
        num_coins = 10000
    else:
        num_coins = 200
    PortfolioHoldings.objects.create(coin_ticker=ticker, number_of_coins=num_coins,
                            amount_in_usd=usd_amt, coin_name=coin_name, type=type_,
                            person=user)
    query = PortfolioHoldings.objects.filter(person=user)
    instance = query.filter(coin_ticker=ticker).first()
    fields = Fields(ticker=ticker, num_coins=coin_amt, usd_amt=usd_amt,
                    coin_name=coin_name, type_=type_)
    new_total = num_coins - coin_amt if fields.type_ == 'Sell' else num_coins + coin_amt
    print(new_total)
    
    pt.update_or_delete(fields, instance, query, new_total, 25000)
    coin = query.filter(coin_ticker=ticker).first()
    if ticker == 'ICX':
        assert float(coin.number_of_coins) == 36000.326
    else:
        assert coin is None