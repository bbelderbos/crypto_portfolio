from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from matplotlib.pyplot import thetagrids
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
    deleted_name = ""
    form = PortfolioForm()
    user = request.user
    user_coins = PortfolioHoldings.objects.filter(person=user)

    if request.method == 'POST':
        user_set = PortfolioHoldings.objects.filter(person=user).filter(coin_name=request.POST['coin_name']).first()
        form = PortfolioForm(request.POST, instance=user_set)

        if form.is_valid():
            type_ = form.cleaned_data['type']
            coin_name = form.cleaned_data['coin_name'].lower()
            ticker = form.cleaned_data['coin_ticker']
            number_of_coins = float(form.cleaned_data['number_of_coins'])
            price = cg.single_coin_data(coin_name).price
            amt_in_usd = number_of_coins * price
            if not user_coins:
                if type_.lower() != 'sell':
                    new_coin = PortfolioHoldings(coin_ticker=ticker, number_of_coins=number_of_coins,
                                amount_in_usd=amt_in_usd, coin_name=coin_name, type=type_, person=user)
                    new_coin.save()
                return HttpResponseRedirect('/portfolio')
            else:
                for coin in PortfolioHoldings.objects.filter(person=user).iterator():
                    new_coin_total = float(coin.number_of_coins) - number_of_coins
                    new_usd_amt = new_coin_total * price
                    if coin.coin_ticker == ticker:
                        if type_.lower() == 'sell':
                            if float(coin.number_of_coins) - number_of_coins > 0:
                                user_coins.filter(coin_ticker=ticker).update(number_of_coins=new_coin_total,
                                                                             amount_in_usd=new_usd_amt)
                            else:
                                deleted_name = coin.coin_ticker
                                user_coins.filter(coin_ticker=ticker).update(amount_in_usd=0.00, number_of_coins=0.00)
                                user_coins.filter(coin_ticker=ticker).first().delete()
                        else:
                            user_coins.filter(coin_ticker=ticker).update(number_of_coins=new_coin_total, amount_in_usd=new_usd_amt)
                
                all_user_coins = [coin.coin_ticker for coin in user_coins.iterator()]
                if ticker not in all_user_coins and ticker != deleted_name and type_.lower() != 'sell':
                    new_coin = PortfolioHoldings(coin_ticker=ticker, number_of_coins=number_of_coins,
                    amount_in_usd=amt_in_usd, coin_name=coin_name, type=type_, person=user)
                    new_coin.save()
        
        return HttpResponseRedirect('/portfolio')


    else:
        all_coins = {c.coin_ticker:float(c.amount_in_usd) for c in user_coins.iterator()}
        data = [int(amt) for amt in all_coins.values()]
        labels = [coin_ticker for coin_ticker in all_coins.keys()]
        pie = portfolio_pie_chart(data, labels)
        display_coins = cg.portfolio_coins(user)
        return render(request, 'portfolio.html', {'pie': pie, 'form': form, 'info': display_coins})

# Comments and Explanation:

# Lots to handle here. 

# user_coins - set as variable to avoid typing out the same model query over and over.
# user_set(lines 39 & 40) - When I added the UNIQUE constraint, it wouldn't let me add the same coin for a different
#     user. By passing in the user_set as an instance, it seemed to only look for the coins that belonged 
#     to that user, and therefore wouldn't update other users' coins. 

# Lines 47-56: If the user didn't already have coins, I had to handle two scenarios. 1). The user accidentally entered Sell, 
# which doesn't make sense....you can't have negative coins. So we only want to save the data if the user enters Buy if 
# they don't already have coins in the system. So if they don't have coins and they didn't enter sell, we save the data
# and return the template. If they enter Sell, we just return the template.


# Lines 57-87: They already have coins in the system. We have to go through their holdings coin by coin and check to see 
# if they coin they entered on the form is in their holdings. If it is, we update it. Then we have to handle Buy or Sell
# there as well. If Sell, we have to update the number of coins and the usd amount. If Buy, we also update, but the update 
# is simpler. 

# I ran into some weird behavior with deleting a coin which is why I needed lines 69-73 and line 80. Basically, it would
# delete the entry, but if I bought again, the old data would reappear and it would say I had the old data + the new data. 
# Running lines 69-73 and the conditional check on line 80 took care of this.

# Lines 79-83: If the user has coins in the system, but not the coin they entered (and it wasn't deleted above...) we 
# save the data. 

# Lines 85-87: The return statement for if the request is POST and the user has coins. 

# Lines 90-93: Return statement for it it's a GET request. 

# I had to use HttpResponseRedirect for the POST request returns because without it, if I just refreshed the page,
# it would submit the form again, and update user data when I don't want it to. 

# You can ignore the "pie" and "all_coins" for now. I need to work on them and they are just there as placeholders so that 
# when I run the server, I see what the page should look like. 

