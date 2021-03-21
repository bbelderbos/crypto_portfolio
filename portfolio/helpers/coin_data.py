from collections import namedtuple
from portfolio.models import PortfolioHoldings

from pycoingecko import CoinGeckoAPI


TOP_COINS = 25
TOP_EXCHANGES = 5
Coin = namedtuple('Coin', 'rank logo name price market_cap volume change percent_change')


class CoinData:
    def __init__(self) -> None:
        self.info = CoinGeckoAPI()
    

    def get_all_coin_data(self, logos):
        top_coins = []
        for idx, item in enumerate(self.info.get_coins_markets('usd')[:TOP_COINS], start=1):
            coin = Coin(rank=idx, logo=logos[idx-1], name=item['id'].title(), price=item['current_price'],
                    market_cap=item['market_cap'], volume=item['total_volume'],
                    change=item['price_change_24h'], percent_change=round(item['price_change_percentage_24h'],2))
            top_coins.append(coin)
        return top_coins


    def single_coin_data(self, coin):
        SingleCoin = namedtuple('SingleCoin', 'id symbol link1 link2 image market_cap_rank ath price mcap volume')
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


    def single_coin_exchanges(self, coin):
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
        coin_list = []
        userCoins = namedtuple('userCoins', 'ticker amount usd image')
        user_coins = PortfolioHoldings.objects.filter(person=user)
        for coin in user_coins.iterator():
            image = self.single_coin_data(coin.coin_name).image
            coin = userCoins(ticker=coin.coin_ticker, amount=coin.number_of_coins, 
                   usd=coin.amount_in_usd, image=image)
            coin_list.append(coin)
        return coin_list