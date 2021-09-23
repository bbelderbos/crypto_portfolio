import pytest
from django.template.loader import render_to_string


@pytest.mark.django_db
@pytest.fixture
def login_user(client, django_user_model):
    """Helper function used to avoid using the same
    code to login a user for every test."""
    username = 'user1'
    password = 'foo'
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)


@pytest.mark.parametrize("route", [
    "/search",
    "/accounts/logout",
    "/accounts/signup",
    "/accounts/login",
    "/portfolio",
    "/404",
    # ""  -> super slow test, leaving out
])
def test_with_authenticated_client(client, login_user, route):
    """Testing view reponses with logged in user
       Jesse is 301 correct for all here?
    """
    response = client.get(route)
    assert response.status_code == 301


@pytest.mark.django_db
def test_home_page_renders_content(client, login_user):
    """Testing to ensure the home page is rendering appropriate
    content"""
    response = client.get('')
    assert b'Welcome to CoinHub!' in response.content


def test_displaypage_access_not_logged_in(client):
    """Testing to ensure that a user that is not
    logged in is redirected away from the portfolio page."""
    response = client.get('/portfolio')
    assert response.status_code == 301


@pytest.mark.django_db
def test_portfoliopage_renders_content(client, login_user):
    """Testing to ensure that content is being rendered to
    a user who is logged in."""
    response = client.get('/portfolio')
    assert response.status_code == 301
    assert 'Enter your purchases or sells.' in render_to_string('portfolio.html')
