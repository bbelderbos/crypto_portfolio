from collections import namedtuple
from portfolio.models import PortfolioHoldings

from pycoingecko import CoinGeckoAPI


TOP_COINS = 25
TOP_EXCHANGES = 5
Coin = namedtuple('Coin', 'rank logo name price market_cap volume change percent_change')
CoinSet = namedtuple('CoinSet', 'ticker amount usd image')
SingleCoin = namedtuple('SingleCoin', 'id symbol link1 link2 image market_cap_rank ath price mcap volume')


class CoinData:
    """Gathers all relevant data from the CoinGecko
    API, and returns it to the app pages."""
    def __init__(self) -> None:
        self.info = CoinGeckoAPI()
        self.all_supported_coins = {c['id'] for c
                                in self.info.get_coins_list()}


    def get_coin_by_ticker(self, coin_ticker):
        """A lookup that is used in case the user passes a
        coin's ticker into the form. Coins are only accessible
        via the API by their id, but users may pass in a ticker
        instead. This method handles that situation."""
        names = {coin['symbol']: coin['id'] 
                for coin in self.info.get_coins_list()}
        return names.get(coin_ticker.lower(), coin_ticker)
        

    def get_all_coin_data(self, logos):
        """This method returns the relevant data for all coins
        in the top 25 coins ranked by market cap."""
        top_coins = []
        for idx, item in enumerate(self.info.get_coins_markets('usd')[:TOP_COINS], start=1):
            coin = Coin(rank=idx, logo=logos[idx-1], name=item['id'].title(), price=item['current_price'],
                    market_cap=item['market_cap'], volume=item['total_volume'],
                    change=item['price_change_24h'], percent_change=round(item['price_change_percentage_24h'],2))
            top_coins.append(coin)
        return top_coins


    def single_coin_data(self, coin):
        """This method gathers all the relevant data for a single
        coin that the user may search for."""
        try:
            data = self.info.get_coin_by_id(coin.lower())
            id = data['id'].title()
            symbol = data['symbol'].upper()
            link1 = data['links']['homepage'][0]
            link2 = data['links']['blockchain_site'][0]
            image = data['image']['small']
            market_cap_rank = data['market_cap_rank']
            price_data = self.info.get_coins_markets('usd')[market_cap_rank-1]
            ath = '$' + str(data['market_data']['ath']['usd'])
            price = price_data['current_price']
            mcap = price_data['market_cap']
            volume = price_data['total_volume']
            return SingleCoin(id=id, symbol=symbol, link1=link1, link2=link2, image=image,
                            market_cap_rank=market_cap_rank, ath=ath, price=price, mcap=mcap, volume=volume)
        except TypeError:
            pass


    def single_coin_exchanges(self, coin):
        """Gathers all relevant exchange data for a
        single coin."""
        exchange_info = []
        Exchanges = namedtuple('Exchanges', 'name volume')
        data = self.info.get_coin_by_id(coin.lower())['tickers']
        names = [name['market']['name'] for name in data if name['target'] == 'USDT']
        volumes = [round(vol['volume'], 2) for vol in data if vol['target'] == 'USDT']
        for i in range(TOP_EXCHANGES):
            exchange = Exchanges(name=names[i], volume=volumes[i])
            exchange_info.append(exchange)
        return exchange_info


    def portfolio_coins(self, user):
        """Gets all of the data for a user's coins
        to display on the portfolio page."""
        coin_list = []
        user_coins = PortfolioHoldings.objects.filter(person=user)
        for coin in user_coins.iterator():
            name = self.get_coin_by_ticker(coin.coin_ticker)
            image = self.single_coin_data(name).image
            coin = CoinSet(ticker=coin.coin_ticker, amount=coin.number_of_coins, 
                   usd=coin.amount_in_usd, image=image)
            coin_list.append(coin)
        return coin_list