import pytest
from django.test import Client
from django.contrib.auth.models import User

from news.models import News, Comment


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def authenticated_client(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def news_post():
    return News.objects.create(title='Test News', text='Test text')


@pytest.fixture
def user_id(authenticated_client):
    return authenticated_client.session.get('_auth_user_id')


@pytest.fixture
def create_comments(news_post, user_id):
    user = User.objects.get(pk=user_id)
    comment = Comment.objects.create(
        news=news_post,
        author=user,
        text='Initial test comment',
        created='2023-02-10 00:00:00'
    )
    return comment
