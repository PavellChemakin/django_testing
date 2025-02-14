import pytest
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth.models import User

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(anonymous_client,
                                            news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = anonymous_client.post(url, {'text': 'Test comment'})
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(text='Test comment').exists()


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(authenticated_client,
                                             news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = authenticated_client.post(url, {'text': 'Test comment'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(text='Test comment').exists()


@pytest.mark.django_db
def test_comment_with_banned_words(authenticated_client, news_post):
    banned_words = ['forbidden', 'banned']
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    comment_text = f'Test {banned_words[0]} comment'
    payload = {'text': comment_text}
    response = authenticated_client.post(url, payload)
    assert response.status_code == HTTPStatus.FOUND
    comment_query = Comment.objects.filter(text=comment_text)
    comment_exists = comment_query.exists()
    assert comment_exists


@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(authenticated_client,
                                                 create_comments):
    url = reverse('news:edit', kwargs={'pk': create_comments.pk})
    new_text = 'Updated test comment'
    response = authenticated_client.post(url, {'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    create_comments.refresh_from_db()
    assert create_comments.text == new_text


@pytest.mark.django_db
def test_authenticated_user_can_delete_own_comment(authenticated_client,
                                                   create_comments):
    url = reverse('news:delete', kwargs={'pk': create_comments.pk})
    response = authenticated_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=create_comments.pk).exists()


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_others_comment(authenticated_client,
                                                       create_comments):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:edit', kwargs={'pk': create_comments.pk})
    response = authenticated_client.post(url, {'text': 'Trying to edit'})
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_others_comment(authenticated_client,
                                                         create_comments):
    other_user = User.objects.create_user(username='otheruser',
                                          password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:delete', kwargs={'pk': create_comments.pk})
    response = authenticated_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
