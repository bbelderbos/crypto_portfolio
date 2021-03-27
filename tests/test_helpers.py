from crypto import __version__
from unittest.mock import Mock, patch
from typing import List, Sequence, Any
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from portfolio.helpers.coin_data import CoinData
from portfolio.helpers.chart import convert_unix_to_date, chart_data, portfolio_pie_chart
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.models import PortfolioHoldings
from portfolio.templatetags.tags import format_money, format_coin_amt

cg = CoinData()

def test_version():
    assert __version__ == '0.1.0'


@pytest.mark.parametrize('unix_time, expected', [
    (1654437715, '2022-06-05'),
    (1543216754, '2018-11-26'),
    (1247213714, '2009-07-10')
])


def test_convert_unix_to_date(unix_time, expected):
    result = convert_unix_to_date(unix_time).split()[0]
    assert result == expected


def test_chart_data():
    coins = ['bitcoin', 'ethereum']
    for coin in coins:
        result = chart_data(coin)
        assert result is not None
        assert 'Price in USD' in result


@pytest.mark.parametrize('data, labels', [
    ([1500, 2500, 10000], ['BTC', 'ETH', 'LINK']),
    ([300, 400, 500], ['DOT', 'VET', 'NEO']),
    ([100_000, 200_000, 300_000], ['LTC', 'SNX', 'EOS'])
])

def test_pie_chart(data, labels):
    result = portfolio_pie_chart(data, labels)
    assert result is not None
    assert 'Coin Names' in result


def test_coin_data_all_coins():
    logos = scrape_coin_logos()
    result = cg.get_all_coin_data(logos)
    names = [r.name for r in result]
    assert len(result) == 25
    assert result[0].name == 'Bitcoin'
    assert result[1].name == 'Ethereum'
    assert 'Theta-Token' in names


@pytest.mark.parametrize('coin, expected', [
    ('icon', ['Icon', 'ICX']),
    ('bitcoin', ['Bitcoin', 'BTC']),
    ('ethereum', ['Ethereum', 'ETH']),
    ('polkadot', ['Polkadot', 'DOT'])
])


def test_single_coin_data(coin, expected):
    result = cg.single_coin_data(coin)
    assert result.id == expected[0]
    assert result.symbol == expected[1]
    assert len(result) == 10


def test_single_coin_exchanges():
    coins = ['bitcoin', 'ethereum', 'litecoin']
    exchanges = []
    for coin in coins:
        result = cg.single_coin_exchanges(coin)
        exchange_names = [r.name.lower() for r in result]
        exchanges.extend(exchange_names)
        assert len(result) == 5
        assert len(result[0]) == 2
    assert 'binance' in exchanges


@pytest.mark.django_db(transaction=True)
def test_portfolio_coins():
    user = User.objects.create_user(username='joe', password='tesTing123%')
    PortfolioHoldings.objects.create(coin_ticker='ICX', number_of_coins=1400.00,
                            amount_in_usd=2800.00, coin_name='icon', type='Buy',
                            person=user)
    result = cg.portfolio_coins(user)
    assert len(result) == 1
    assert result[0].ticker == 'ICX'
    assert str(result[0].usd) == '2800.00'
    assert PortfolioHoldings.objects.filter(person=user).first().coin_ticker == 'ICX'


def test_coin_logos():
    result = scrape_coin_logos()
    assert len(result) == 25
    assert 'assets' in result[0]


@pytest.mark.parametrize('number, expected', [
    (350000.45, '$350,000.45'),
    (2300.42, '$2,300.42'),
    (10007.42, '$10,007.42'),
    ('dog', 'dog')
])


def test_format_money(number, expected):
    result = format_money(number)
    assert result == expected


@pytest.mark.parametrize('number, expected', [
    (Decimal('350000.450720000'), '350000.45072'),
    (Decimal('45.00001003000'), '45.00001003'),
    (Decimal('320.096500200000'), '320.0965002'),
    (Decimal('0.00'), '0'),
    (Decimal('500.000000000000000000'), '500')
])


def test_format_coin_amt(number, expected):
    result = format_coin_amt(number)
    assert result == expected