import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.utils.timezone import make_aware, datetime

from news.models import News, Comment


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def get_user():
    user = User.objects.create_user(username='testuser', password='testpass')
    return user


@pytest.fixture
def authenticated_client(db, get_user):
    client = Client()
    client.force_login(get_user)
    return client


@pytest.fixture
def news_post():
    return News.objects.create(title='Test News', text='Test text')


@pytest.fixture
def create_comments(news_post, get_user):
    user = get_user
    comment = Comment.objects.create(
        news=news_post,
        author=user,
        text='Initial test comment',
        created='2023-02-10 00:00:00'
    )
    return comment


@pytest.fixture
def create_multiple_comments(news_post, get_user):
    user = get_user
    comments = []

    for i in range(3):
        created_time = make_aware(datetime(2023, 2, 10 + i, 0, 0, 0))
        comment = Comment.objects.create(
            news=news_post,
            author=user,
            text=f'Test comment {i+1}',
            created=created_time
        )
        comments.append(comment)

    return comments
