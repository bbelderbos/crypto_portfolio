from django import forms
from django.db.models import fields
from .models import PortfolioHoldings

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioHoldings
        widgets = {
            'coin_name': forms.TextInput(attrs={'placeholder': 'Coin (Ticker Symbol)'}),
            'number_of_coins': forms.TextInput(attrs={'placeholder': 'Enter Amount of Coins Bought'}),
            'amount_in_usd': forms.TextInput(attrs={'placeholder': 'Enter USD value'}),
            'type': forms.TextInput(attrs={'placeholder': 'Buy or Sell'})
        }
        fields = ['coin_name', 'number_of_coins', 'amount_in_usd', 'type']