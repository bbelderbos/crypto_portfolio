from collections import namedtuple

from unittest.mock import Mock, patch
from typing import List, Sequence, Any
from django.db.models import query

import pytest
from django.contrib.auth.models import User

from portfolio.helpers.coin_data import CoinData
from portfolio.helpers.chart import convert_unix_to_date, chart_data, portfolio_pie_chart
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.helpers.portfolio import Portfolio
from portfolio.models import PortfolioHoldings
from .conftest import setup_user, coins

Fields = namedtuple('Fields', 'ticker num_coins usd_amt coin_name type_')
cg = CoinData()


@pytest.mark.django_db(transaction=True)
def create_user_and_class_instance():
    user = User.objects.create_user(username='joe', password='tesTing123%')
    pt = Portfolio(user)
    coin = PortfolioHoldings.objects.create(coin_ticker='NEO', number_of_coins='51',
                            amount_in_usd='2000.00', coin_name='neo', type='Buy',
                            person=user)
    query = PortfolioHoldings.objects.filter(person=user)
    return user, pt, query


@pytest.mark.django_db(transaction=True)
def test_no_user_coins(coins):
    user, pt, query = create_user_and_class_instance()
    for coin in coins:
        pt.no_user_coins(coin.ticker, coin.num_coins, coin.usd_amt, coin.coin_name, coin.type_)
        coin = query.filter(coin_ticker=coin.ticker).first()
        assert coin is None or coin.coin_ticker == 'ICX'


@pytest.mark.parametrize('ticker, num_coins, usd_amt, coin_name, type_', [
    ('ICX', 26000.326, 52000.35, 'icon', 'Buy'),
    ('DOT', 300, 9000, 'DOT', 'Sell')
])
@pytest.mark.django_db(transaction=True)
def test_no_user_coins2(ticker, num_coins, usd_amt, coin_name, type_):
    user, pt, query = create_user_and_class_instance()
    pt.no_user_coins(ticker, num_coins, usd_amt, coin_name, type_)
    coin = query.filter(coin_ticker=ticker).first()
    assert coin is None or coin.coin_ticker == 'ICX'


@pytest.mark.parametrize('ticker, num_coins, usd_amt, coin_name, type_', [
    ('ICX', 26000.326, 52000.35, 'icon', 'Buy'),
    ('DOT', 300, 9000, 'DOT', 'Sell')
])
@pytest.mark.django_db(transaction=True)
def test_delete_coin(ticker, num_coins, usd_amt, coin_name, type_):
    user, pt, query = create_user_and_class_instance()
    PortfolioHoldings.objects.create(coin_ticker=ticker, number_of_coins=num_coins,
                            amount_in_usd=usd_amt, coin_name=coin_name, type=type_,
                            person=user)

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
    user, pt, query = create_user_and_class_instance()
    num_coins = 10000 if ticker == 'ICX' else 200
    PortfolioHoldings.objects.create(coin_ticker=ticker, number_of_coins=num_coins,
                            amount_in_usd=usd_amt, coin_name=coin_name, type=type_,
                            person=user)

    instance = query.filter(coin_ticker=ticker).first()
    fields = Fields(ticker=ticker, num_coins=coin_amt, usd_amt=usd_amt,
                    coin_name=coin_name, type_=type_)
    new_total = num_coins - coin_amt if fields.type_ == 'Sell' else num_coins + coin_amt

    pt.update_or_delete(fields, instance, query, new_total, 25000)
    coin = query.filter(coin_ticker=ticker).first()
    assert coin is None or float(coin.number_of_coins) == 36000.326



@pytest.mark.parametrize('amt_in_usd, fields', [
    (150000.37,
    Fields(ticker='ETH', num_coins=200, usd_amt=15000, coin_name='ethereum',
    type_='Sell')),
    (35000,
    Fields(ticker='RSR', num_coins=200, usd_amt=15000, coin_name='neo',
    type_='Buy'))
])
@pytest.mark.django_db(transaction=True)
def test_save_new_coin(amt_in_usd, fields):
    user, pt, query = create_user_and_class_instance()
    if fields.ticker == 'ETH':
        PortfolioHoldings.objects.create(coin_ticker='ETH', number_of_coins=200,
                            amount_in_usd=15000, coin_name='ethereum', type='Sell',
                            person=user)
    else:
        PortfolioHoldings.objects.create(coin_ticker='AAVE', number_of_coins=200,
                            amount_in_usd=15000, coin_name='aave', type='Buy',
                            person=user)

    pt.save_new_coin(fields, user, query, amt_in_usd)
    coin = query.filter(coin_ticker=fields.ticker).first()
    assert float(coin.amount_in_usd) in {15000, 35000.00}

