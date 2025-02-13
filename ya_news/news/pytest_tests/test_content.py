import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def authenticated_client():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def create_news_posts():
    for i in range(15):
        News.objects.create(
            title=f'Test News {i}',
            text=f'Test text {i}',
            date=f'2023-02-{i+1}'
        )


@pytest.fixture
def create_comments(news_post, authenticated_client):
    user = authenticated_client.session.get('_auth_user_id')
    for i in range(5):
        Comment.objects.create(news=news_post, author_id=user,
                               text=f'Test comment {i}',
                               created=f'2023-02-10 {i}:00:00')


@pytest.mark.django_db
def test_home_page_news_count(anonymous_client, create_news_posts):
    url = reverse('news:home')
    response = anonymous_client.get(url)
    object_list = response.context['object_list']
    object_list_length = len(object_list)
    max_news_count = settings.NEWS_COUNT_ON_HOME_PAGE

    assert object_list_length <= max_news_count


@pytest.mark.django_db
def test_news_sorted_by_date(anonymous_client, create_news_posts):
    url = reverse('news:home')
    response = anonymous_client.get(url)
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert list(reversed(sorted(dates))) == dates
