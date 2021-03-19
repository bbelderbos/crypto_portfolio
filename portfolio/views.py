from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import PortfolioHoldings
from .forms import PortfolioForm

from portfolio.helpers.chart import chart_data, portfolio_pie_chart
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.helpers.coin_data import CoinData

cg = CoinData()

def homepage(request):
    top_coins = cg.get_all_coin_data(scrape_coin_logos())
    return render(request, 'home.html', {'top_coins': top_coins})


@csrf_exempt
def searchpage(request):
    if request.method == 'POST':
        coin = request.POST['coin'].lower()
        chart = chart_data(coin)
        data = cg.single_coin_data(coin)
        exchanges = cg.single_coin_exchanges(coin)
        return render(request, 'search.html', {'chart': chart, 'data': data, 'exchanges': exchanges})
    return render(request, 'search.html')


@login_required
def portfolio_page(request):
    form = PortfolioForm()
    user = request.user
    # user_coins = PortfolioHoldings.objects.filter(person=user)

    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            type_ = request.POST['type']
            coin_name = request.POST['coin_name']
            number_of_coins = float(request.POST['number_of_coins'])
            price = cg.single_coin_data(coin_name).price
            amt_in_usd = number_of_coins * price
            if not PortfolioHoldings.objects.filter(person=user):
                all_coins = PortfolioHoldings(coin_name=coin_name, number_of_coins=number_of_coins,
                             amount_in_usd=amt_in_usd, type=type_, person=user)
                all_coins.save()
                user_coins = [c for c in PortfolioHoldings.objects.filter(person=user).iterator()]
                print('yes')
                pie = portfolio_pie_chart()
                return render(request, 'portfolio.html', {'pie': pie, 'form': form})
            else:
                print('this user has data')
                #coin_to_update = PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name)
                for coin in PortfolioHoldings.objects.filter(person=user).iterator():
                    if coin.coin_name == coin_name:
                        if type_.lower() == 'sell':
                            if float(coin.number_of_coins) - number_of_coins >= 0:
                                new_coin_total = float(coin.number_of_coins) - number_of_coins
                                PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name).update(number_of_coins=new_coin_total)
                                new_usd_amt = new_coin_total * price
                                if new_usd_amt >= 0:
                                    PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name).update(amount_in_usd=new_usd_amt)
                                else:
                                    PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name).update(amount_in_usd=0.00)
                            else:
                                PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name).delete()
                        else:
                            new_coin_total = coin.number_of_coins + number_of_coins
                            new_usd_amt = new_coin_total * price
                            PortfolioHoldings.objects.filter(person=user).filter(coin_name=coin_name).update(number_of_coins=new_coin_total, amount_in_usd=new_usd_amt)
                    else:
                        all_coins = PortfolioHoldings(coin_name=coin_name, number_of_coins=number_of_coins,
                        amount_in_usd=amt_in_usd, type=type_, person=user)
                        all_coins.save()
                        
        pie = portfolio_pie_chart()
        all_coins = [c for c in PortfolioHoldings.objects.filter(person=user).iterator()]
        return render(request, 'portfolio.html', {'pie': pie, 'form': form})


    else:
        pie = portfolio_pie_chart()
        all_coins = [c for c in PortfolioHoldings.objects.filter(person__id=user.id).iterator()]
        return render(request, 'portfolio.html', {'pie': pie, 'form': form})
