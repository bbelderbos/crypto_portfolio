from collections import namedtuple
from portfolio.models import PortfolioHoldings
from portfolio.forms import PortfolioForm
from portfolio.helpers.chart import portfolio_pie_chart as pie_chart
from portfolio.helpers.coin_data import CoinData


FormData = namedtuple('FormData', 'ticker num_coins coin_name type_')
cg = CoinData()

class Portfolio:
    def __init__(self, user) -> None:
        self.user = user
    

    def create_user_set(self, coin):
        return PortfolioHoldings.objects.filter(person=self.user).filter(coin_name=coin).first()
    

    def no_user_coins(self, ticker, num_coins, usd_amt, coin_name, type_):
        if type_.lower() != 'sell':
            new_coin = PortfolioHoldings(coin_ticker=ticker, number_of_coins=num_coins,
                        amount_in_usd=usd_amt, coin_name=coin_name, type=type_, person=self.user)
            new_coin.save()

    
    def get_form_data(self, form):
        return FormData(ticker=form.cleaned_data['coin_ticker'],
                        num_coins=float(form.cleaned_data['number_of_coins']),
                        coin_name=form.cleaned_data['coin_name'],
                        type_=form.cleaned_data['type'])
    

    def delete_coin(self, user_coins, fields):
        user_coins.filter(coin_ticker=fields.ticker).update(amount_in_usd=0.00, number_of_coins=0.00)
        user_coins.filter(coin_ticker=fields.ticker).first().delete()
    

    def update_or_delete(self, fields, coin, user_coins, new_total, new_usd):
        if fields.type_.lower() == 'sell':
            if float(coin.number_of_coins) - fields.num_coins > 0:
                user_coins.filter(coin_ticker=fields.ticker).update(number_of_coins=new_total,
                                                                amount_in_usd=new_usd)
            else:
                self.delete_coin(user_coins, fields)
        else:
            user_coins.filter(coin_ticker=fields.ticker).update(number_of_coins=new_total, amount_in_usd=new_usd)
    

    def save_new_coin(self, fields, deleted_name, user, user_coins, amt_in_usd):
        all_user_coins = [coin.coin_ticker for coin in user_coins.iterator()]
        if fields.ticker not in all_user_coins and fields.ticker != deleted_name and fields.type_.lower() != 'sell':
            new_coin = PortfolioHoldings(coin_ticker=fields.ticker, number_of_coins=fields.num_coins,
            amount_in_usd=amt_in_usd, coin_name=fields.coin_name, type=fields.type_, person=user)
            new_coin.save()
    

    def package_data_and_render(self, user_coins):
        all_coins = {c.coin_ticker:float(c.amount_in_usd) for c in user_coins.iterator()}
        data = [int(amt) for amt in all_coins.values()]
        labels = [coin_ticker for coin_ticker in all_coins.keys()]
        pie = pie_chart(data, labels)
        display_coins = cg.portfolio_coins(self.user)
        return pie, display_coins
    

    def find_coin(self, fields, user_coins, price):
        c = user_coins.filter(coin_ticker=fields.ticker).first()
        if c:
            new_coin_total = float(c.number_of_coins) - fields.num_coins
            new_usd_amt = new_coin_total * price
            self.update_or_delete(fields, c, user_coins, new_coin_total, new_usd_amt)
            return None
        