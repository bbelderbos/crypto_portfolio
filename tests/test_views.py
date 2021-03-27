from collections import namedtuple
import pytest
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from portfolio.models import PortfolioHoldings

@pytest.mark.django_db
def login_user(client, django_user_model):
    """Helper function used to avoid using the same
    code to login a user for every test."""
    username = 'user1'
    password = 'foo'
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)


def test_with_authenticated_client(client, django_user_model):
    """Testing with a simulated, logged in user, that the response
    codes will either be 200 or redirects (301,302)"""
    login_user(client, django_user_model)
    views = '/search /accounts/logout /accounts/signup /accounts/login /portfolio /404'.split()
    for view in views:
        response = client.get(view)
        assert response.status_code in {200, 301, 302}
    assert client.get('').status_code == 200


@pytest.mark.django_db
def test_home_page_renders_content(client, django_user_model):
    """Testing to ensure the home page is rendering appropriate
    content"""
    login_user(client, django_user_model)
    response = client.get('')
    assert b'Welcome to CoinHub!' in response.content


def test_displaypage_access_not_logged_in(client):
    """Testing to ensure that a user that is not
    logged in is redirected away from the portfolio page."""
    response = client.get('/portfolio')
    assert response.status_code == 301


@pytest.mark.django_db
def test_portfoliopage_renders_content(client, django_user_model):
    """Testing to ensure that content is being rendered to
    a user who is logged in."""
    login_user(client, django_user_model)
    response = client.get('/portfolio')
    assert response.status_code == 301
    assert 'Enter your purchases or sells.' in render_to_string('portfolio.html')