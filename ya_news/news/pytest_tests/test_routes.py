import pytest
from django.urls import reverse
from django.contrib.auth.models import User


def home_url():
    return reverse('news:home')


def news_detail_url(news_post):
    return reverse('news:detail', kwargs={'pk': news_post.pk})


def comment_delete_url(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})


def comment_edit_url(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})


def signup_url():
    return reverse('users:signup')


def login_url():
    return reverse('users:login')


def logout_url():
    return reverse('users:logout')


@pytest.mark.django_db
def test_home_page_anonymous(anonymous_client):
    url = home_url()
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_page_anonymous(anonymous_client, news_post):
    url = news_detail_url(news_post)
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_delete_page_authenticated(authenticated_client,
                                           create_comments):
    url = comment_delete_url(create_comments)
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_page_authenticated(authenticated_client,
                                         create_comments):
    url = comment_edit_url(create_comments)
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_delete_page_anonymous(anonymous_client,
                                       create_comments):
    url = comment_delete_url(create_comments)
    response = anonymous_client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_comment_edit_page_anonymous(anonymous_client,
                                     create_comments):
    url = comment_edit_url(create_comments)
    response = anonymous_client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_comment_delete_page_wrong_user(authenticated_client, create_comments):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = comment_delete_url(create_comments)
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_comment_edit_page_wrong_user(authenticated_client, create_comments):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = comment_edit_url(create_comments)
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_registration_page_anonymous(anonymous_client):
    url = signup_url()
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_anonymous(anonymous_client):
    url = login_url()
    response = anonymous_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_page_anonymous(anonymous_client):
    url = logout_url()
    response = anonymous_client.get(url)
    assert response.status_code == 200
