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
def test_anonymous_user_cannot_post_comment(anonymous_client, news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = anonymous_client.post(url, {'text': 'Test comment'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(authenticated_client, news_post):
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    response = authenticated_client.post(url, {'text': 'Test comment'})
    assert response.status_code == 302
    assert Comment.objects.filter(text='Test comment').exists()


@pytest.mark.django_db
def test_comment_with_banned_words(authenticated_client, news_post):
    banned_words = ['forbidden', 'banned']
    url = reverse('news:detail', kwargs={'pk': news_post.pk})
    comment_text = f'Test {banned_words[0]} comment'
    payload = {'text': comment_text}
    response = authenticated_client.post(url, payload)
    assert response.status_code == 302
    comment_query = Comment.objects.filter(text=comment_text)
    comment_exists = comment_query.exists()
    assert comment_exists


@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(authenticated_client,
                                                 comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Updated test comment'
    response = authenticated_client.post(url, {'text': new_text})
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_authenticated_user_can_delete_own_comment(authenticated_client,
                                                   comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = authenticated_client.post(url)
    assert response.status_code == 302
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_others_comment(authenticated_client,
                                                       comment):
    other_user = User.objects.create_user(username='otheruser', password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = authenticated_client.post(url, {'text': 'Trying to edit'})
    assert response.status_code == 404


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_others_comment(authenticated_client,
                                                         comment):
    other_user = User.objects.create_user(username='otheruser', password='otherpass')
    authenticated_client.force_login(other_user)
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = authenticated_client.post(url)
    assert response.status_code == 404
