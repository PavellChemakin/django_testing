from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from notes.models import Note


class RouteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.client.force_login(self.user)

        self.urls = {
            'list': 'notes:list',
            'success': 'notes:success',
            'add': 'notes:add',
            'detail': 'notes:detail',
            'edit': 'notes:edit',
            'delete': 'notes:delete',
            'signup': '/auth/signup/',
            'login': '/auth/login/',
            'logout': '/auth/logout/'
        }

    def test_home_page_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_pages(self):
        for url_name in ['list', 'success', 'add']:
            response = self.client.get(reverse(self.urls[url_name]))
            self.assertEqual(response.status_code, 200)

    def test_note_detail_update_delete_pages(self):
        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user
        )
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(reverse(self.urls[url_name],
                                               args=[note.slug]))
            self.assertEqual(response.status_code, 200)

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
        self.client.force_login(other_user)
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(reverse(self.urls[url_name],
                                               args=[note.slug]))
            self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirect(self):
        self.client.logout()
        for url_name in ['list', 'success', 'add']:
            response = self.client.get(reverse(self.urls[url_name]))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response, f"/auth/login/?next={reverse(self.urls[url_name])}")

        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user
        )
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(reverse(self.urls[url_name],
                                               args=[note.slug]))
            self.assertEqual(response.status_code, 302)
            next_url = reverse(self.urls[url_name], args=[note.slug])
            login_url = f"/auth/login/?next={next_url}"
            self.assertRedirects(response, login_url)

    def test_public_pages_available_to_all(self):
        self.client.logout()
        for url_name in ['signup', 'login', 'logout']:
            response = self.client.get(self.urls[url_name])
            self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user)
        for url_name in ['signup', 'login', 'logout']:
            response = self.client.get(self.urls[url_name])
            self.assertEqual(response.status_code, 200)
