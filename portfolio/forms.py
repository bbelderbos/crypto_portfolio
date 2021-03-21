from django import forms
from .models import PortfolioHoldings

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioHoldings
        widgets = {
            'coin_ticker': forms.TextInput(attrs={'placeholder': 'Coin (Ticker Symbol)'}),
            'number_of_coins': forms.TextInput(attrs={'placeholder': 'Enter Amount of Coins Bought'}),
            'coin_name': forms.TextInput(attrs={'placeholder': 'Enter the coin name'}),
            'type': forms.TextInput(attrs={'placeholder': 'Buy or Sell'})
        }
        fields = ['coin_ticker', 'number_of_coins', 'coin_name', 'type']