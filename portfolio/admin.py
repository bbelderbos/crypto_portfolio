from django.contrib import admin
from .models import PortfolioHoldings

models = [PortfolioHoldings]
admin.site.register(models)
