from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from matplotlib.pyplot import thetagrids
from .models import PortfolioHoldings
from .forms import PortfolioForm, ErrorRedirect

from portfolio.helpers.chart import chart_data, portfolio_pie_chart
from portfolio.helpers.scrape_logos import scrape_coin_logos
from portfolio.helpers.coin_data import CoinData
from portfolio.helpers.portfolio import Portfolio

cg = CoinData()

def homepage(request):
    top_coins = cg.get_all_coin_data(scrape_coin_logos())
    return render(request, 'home.html', {'top_coins': top_coins})


@csrf_exempt
def searchpage(request):
    if request.method == 'POST':
        try:
            coin = cg.get_coin_by_ticker(request.POST['coin'].lower())
            chart = chart_data(coin)
            data = cg.single_coin_data(coin)
            exchanges = cg.single_coin_exchanges(coin)
            return render(request, 'search.html', {'chart': chart, 'data': data, 'exchanges': exchanges})
        except Exception:
            return HttpResponseRedirect('/404')
    return render(request, 'search.html')


@login_required
def portfolio_page(request):
    form = PortfolioForm()
    user = request.user
    user_coins = PortfolioHoldings.objects.filter(person=user)
    pt = Portfolio(user)

    if request.method == 'GET':
        pie, display_coins = pt.package_data_and_render(user_coins)
        return render(request, 'portfolio.html', {'pie': pie, 'form': form, 'info': display_coins})
    
    user_set = pt.create_user_set(request.POST['coin_name'])
    form = PortfolioForm(request.POST, instance=user_set)
    if form.is_valid():
        fields = pt.get_form_data(form)
        try:
            alt_name = cg.get_coin_by_ticker(fields.ticker)
            price = cg.single_coin_data(alt_name).price
        except (AttributeError, ValueError, TypeError) as e:
            return HttpResponseRedirect('/404')
        amt_in_usd = fields.num_coins * price

        if not user_coins:
            pt.no_user_coins(fields.ticker, fields.num_coins, amt_in_usd, fields.coin_name, fields.type_)
            return HttpResponseRedirect('/portfolio')
        else:
            query = pt.find_coin_in_user_group(fields, user_coins, price)
            if not query:
                pt.save_new_coin(fields, user, user_coins, amt_in_usd)
            return HttpResponseRedirect('/portfolio')


def error_page(request):
    button = ErrorRedirect()
    return render(request, '404.html', {'button': button})