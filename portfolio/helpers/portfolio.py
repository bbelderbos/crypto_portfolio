from collections import namedtuple
from portfolio.models import PortfolioHoldings
from portfolio.forms import PortfolioForm
from portfolio.helpers.chart import portfolio_pie_chart as pie_chart
from portfolio.helpers.coin_data import CoinData


FormData = namedtuple('FormData', 'ticker num_coins coin_name type_')
SELL = 'sell'
cg = CoinData()

class Portfolio:
    """Class created to handle all of the portfolio page operations.
    Determines whether to save a new coin, or update or delete an 
    existing entry."""
    def __init__(self, user) -> None:
        self.user = user
    

    def create_user_set(self, coin):
        """creates a user instance for the form on the portfolio page
        so that only the user's specific coins will be accessed, and not
        other user's coins by the same name."""
        return PortfolioHoldings.objects.filter(person=self.user).filter(coin_name=coin).first()
    

    def no_user_coins(self, ticker, num_coins, usd_amt, coin_name, type_):
        """Saves a new user's coins to the db."""
        if type_.lower() != SELL:
            new_coin = PortfolioHoldings(coin_ticker=ticker, number_of_coins=num_coins,
                        amount_in_usd=usd_amt, coin_name=coin_name, type=type_, person=self.user)
            new_coin.save()

    
    def get_form_data(self, form):
        """"Collects all form data passed in for easy access."""
        return FormData(ticker=form.cleaned_data['coin_ticker'],
                        num_coins=abs(float(form.cleaned_data['number_of_coins'])),
                        coin_name=form.cleaned_data['coin_name'],
                        type_=form.cleaned_data['type'])
    

    def delete_coin(self, user_coins, fields):
        """Delete's a user's coin from the db if they have sold all of
        that particular coin."""
        user_coins.filter(coin_ticker=fields.ticker).update(amount_in_usd=0.00, number_of_coins=0.00)
        user_coins.filter(coin_ticker=fields.ticker).first().delete()
    

    def update_or_delete(self, fields, coin, user_coins, new_total, new_usd):
        """Determines whether to update or delete a user's coin, based on
        the data they entered into the form."""
        if fields.type_.lower() == SELL:
            if float(coin.number_of_coins) - fields.num_coins > 0:
                user_coins.filter(coin_ticker=fields.ticker).update(number_of_coins=new_total,
                                                                amount_in_usd=new_usd)
            else:
                self.delete_coin(user_coins, fields)
        else:
            user_coins.filter(coin_ticker=fields.ticker).update(number_of_coins=new_total, amount_in_usd=new_usd)
    

    def save_new_coin(self, fields, user, user_coins, amt_in_usd):
        """Determines whether or not a user is adding a new coin
        to the db and, if they are, saves the information to the db."""
        all_user_coins = [coin.coin_ticker for coin in user_coins]
        if fields.ticker not in all_user_coins and fields.type_.lower() != SELL:
            new_coin = PortfolioHoldings(coin_ticker=fields.ticker, number_of_coins=fields.num_coins,
            amount_in_usd=amt_in_usd, coin_name=fields.coin_name, type=fields.type_, person=user)
            new_coin.save()
    

    def package_data_and_render(self, user_coins):
        """Collects all display data for the portfolio page
        and returns it to be used in the page."""
        all_coins = {c.coin_ticker:float(c.amount_in_usd) for c in user_coins}
        data = [int(amt) for amt in all_coins.values()]
        labels = [coin_ticker for coin_ticker in all_coins.keys()]
        pie = pie_chart(data, labels)
        display_coins = cg.portfolio_coins(self.user)
        return pie, display_coins
    

    def find_coin_in_user_group(self, fields, user_coins, price):
        """Determines whether or not a user already has the coin
        they entered into the form. If they do, calls the update
        or delete method to determine whether or not to update the
        coin or delete it. Returns a boolean in case the coin is not
        found in the user's data."""
        c = user_coins.filter(coin_ticker=fields.ticker).first()
        if c:
            if fields.type_.lower() == SELL:
                new_coin_total = float(c.number_of_coins) - fields.num_coins
            else:
                new_coin_total = float(c.number_of_coins) + fields.num_coins
            new_usd_amt = new_coin_total * price
            self.update_or_delete(fields, c, user_coins, new_coin_total, new_usd_amt)
            return True
        return False
