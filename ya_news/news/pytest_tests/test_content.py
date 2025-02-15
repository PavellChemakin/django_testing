from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment, News

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_single_news_in_object_list(anonymous_client, news_post):
    url = HOME_URL
    response = anonymous_client.get(url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context.get('object_list', [])
    assert object_list.count() <= 10


@pytest.mark.django_db
def test_user_sees_only_own_news(authenticated_client, create_multiple_news):
    response = authenticated_client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_list, _ = create_multiple_news
    assert set(news_list) == set(object_list)


@pytest.mark.django_db
def test_news_creation_page_has_form(authenticated_client, news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = authenticated_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context


@pytest.mark.django_db
def test_news_edit_page_has_form(authenticated_client, news_post):
    url = reverse('news:edit', kwargs={'pk': news_post.pk})
    response = authenticated_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comments_sorted_chronologically(authenticated_client,
                                         create_multiple_comments):
    news_pk = create_multiple_comments[0].news.pk
    url = reverse('news:detail', kwargs={'pk': news_pk})
    response = authenticated_client.get(url)
    assert response.status_code == HTTPStatus.OK
    expected_comments = list(
        Comment.objects
        .filter(news__pk=news_pk)
        .order_by('created')
    )
    comments = list(response.context['news'].comment_set.all())
    assert comments == expected_comments


@pytest.mark.django_db
def test_news_sorted_chronologically(authenticated_client,
                                     create_multiple_news):
    response = authenticated_client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_list, _ = create_multiple_news
    expected_news = list(News.objects.all().order_by('-date'))
    assert list(object_list) == expected_news


@pytest.mark.django_db
def test_anonymous_user_cannot_see_comment_form(anonymous_client,
                                                news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = anonymous_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authenticated_user_can_see_comment_form(authenticated_client,
                                                 news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = authenticated_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
