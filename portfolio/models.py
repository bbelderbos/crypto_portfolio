from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

class PortfolioHoldings(models.Model):
    coin_name = models.CharField(max_length=100)
    number_of_coins = models.DecimalField(decimal_places=10,
                        editable=True, max_digits=18)
    amount_in_usd = models.DecimalField(decimal_places=2,
                    editable=True, max_digits=18)
    type = models.CharField(max_length=10, null=False, blank=False, default='Buy')
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='person')

