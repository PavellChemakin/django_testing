import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

from news.models import News


@pytest.fixture
def authenticated_client(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    client.user = user
    return client


@pytest.mark.django_db
def test_single_news_in_object_list(anonymous_client, news_post):
    url = reverse('news:home')
    response = anonymous_client.get(url)
    assert response.status_code == 200
    object_list = response.context.get('object_list', [])
    assert len(object_list) > 0
    assert all(isinstance(item, News) for item in object_list)


@pytest.mark.django_db
def test_user_sees_only_own_news(authenticated_client):
    url = reverse('news:home')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    object_list = response.context['object_list']
    all_news = News.objects.all()
    assert set(object_list) == set(all_news)


@pytest.mark.django_db
def test_news_creation_page_has_form(authenticated_client, news_post):
    news = News.objects.first()
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_news_edit_page_has_form(authenticated_client, news_post):
    news = News.objects.first()
    url = reverse('news:edit', kwargs={'pk': news.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 404
