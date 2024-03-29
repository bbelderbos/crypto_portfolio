from django import forms
from .models import PortfolioHoldings

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioHoldings
        TYPE_CHOICES = (
            ('Buy', 'Buy'),
            ('Sell', 'Sell')
        )
        widgets = {
            'coin_ticker': forms.TextInput(attrs={'placeholder': 'Coin (Ticker Symbol)'}),
            'number_of_coins': forms.TextInput(attrs={'placeholder': 'Enter Amount of Coins Bought'}),
            'coin_name': forms.TextInput(attrs={'placeholder': 'Enter the coin name'}),
            'type': forms.Select(choices=TYPE_CHOICES, attrs={'placeholder': 'Buy or Sell'})
        }
        fields = ['coin_ticker', 'number_of_coins', 'coin_name', 'type']


class ErrorRedirect(forms.Form):
    button = forms.CharField()