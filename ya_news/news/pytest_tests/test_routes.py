import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

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
def news_post():
    return News.objects.create(title='Test News', text='Test text')


@pytest.fixture
def comment(news_post, authenticated_client):
    user = authenticated_client.session.get('_auth_user_id')
    return Comment.objects.create(news=news_post,
                                  author_id=user, text='Test comment')


@pytest.mark.django_db
def test_home_page_anonymous(anonymous_client):
    url = reverse('news:home')
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_page_anonymous(anonymous_client, news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_delete_page_authenticated(authenticated_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_page_authenticated(authenticated_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_delete_page_anonymous(anonymous_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = anonymous_client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_comment_edit_page_anonymous(anonymous_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = anonymous_client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_comment_delete_page_wrong_user(authenticated_client, comment):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_comment_edit_page_wrong_user(authenticated_client, comment):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_registration_page_anonymous(anonymous_client):
    url = reverse('users:signup')
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_anonymous(anonymous_client):
    url = reverse('users:login')
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_page_anonymous(anonymous_client):
    url = reverse('users:logout')
    response = anonymous_client.get(url)
    assert response.status_code == 200
