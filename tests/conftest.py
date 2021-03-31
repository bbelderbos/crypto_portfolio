from collections import namedtuple

from django.contrib.auth.models import User
import pytest

from portfolio.helpers.portfolio import Portfolio
from portfolio.models import PortfolioHoldings

MyCoin = namedtuple('MyCoin', 'ticker num_coins usd_amt coin_name type_')



@pytest.mark.django_db(trasaction=True)
@pytest.fixture(scope='module')
def setup_user():
    user = User.objects.create_user(username='joe', password='tesTing123%')
    pt = Portfolio(user)
    coin = PortfolioHoldings.objects.create(coin_ticker='NEO', number_of_coins='51',
                            amount_in_usd='2000.00', coin_name='neo', type='Buy',
                            person=user)
    query = PortfolioHoldings.objects.filter(person=user)
    return user, pt, query



@pytest.fixture(scope='module')
def coins():
    return [
        MyCoin(ticker='ICX', num_coins=26000.326, usd_amt=52000.35, coin_name='icon', type_='Buy'),
        MyCoin(ticker='DOT', num_coins=300, usd_amt=9000, coin_name='DOT', type_='Sell')
    ]

