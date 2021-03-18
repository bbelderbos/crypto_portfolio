from django.urls import path
from .views import homepage, searchpage, portfolio_page


urlpatterns = [
    path('', homepage, name='home'),
    path('search/', searchpage, name='search'),
    path('portfolio/', portfolio_page, name='portfolio'),
]