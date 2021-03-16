from django.urls import path
from .views import homepage, searchpage


urlpatterns = [
    path('', homepage, name='home'),
    path('search/', searchpage, name='search')
]