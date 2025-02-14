import unittest
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify

from notes.models import Note


def generate_unique_slug(title):
    slug = slugify(title)
    counter = 1
    while Note.objects.filter(slug=slug).exists():
        slug = f"{slugify(title)}-{counter}"
        counter += 1
    return slug


class RouteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.client.force_login(self.user)
        title = "Test Note"
        self.slug = generate_unique_slug(title)
        self.note = Note.objects.create(title=title,
                                        text="This is a test note.",
                                        author=self.user, slug=self.slug)
        self.urls = {
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'success': reverse('notes:success'),
            'add': reverse('notes:add'),
            'detail': reverse('notes:detail', kwargs={'slug': self.note.slug}),
            'edit': reverse('notes:edit', kwargs={'slug': self.note.slug}),
            'delete': reverse('notes:delete', kwargs={'slug': self.note.slug}),
            'signup': reverse('users:signup'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout')
        }

    def test_home_page_anonymous(self):
        self.client.logout()
        response = self.client.get(self.urls['home'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages(self):
        for url_name in ['list', 'success', 'add']:
            response = self.client.get(self.urls[url_name])
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_update_delete_pages(self):
        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user,
            slug=generate_unique_slug('Test Note')
        )
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(self.urls[url_name],
                                       kwargs={'slug': note.slug})
            self.assertEqual(response.status_code, HTTPStatus.OK)

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
        self.client.force_login(other_user)
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(self.urls[url_name],
                                       kwargs={'slug': note.slug})
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirect(self):
        self.client.logout()
        for url_name in ['list', 'success', 'add']:
            response = self.client.get(self.urls[url_name])
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response, f"/auth/login/?next={self.urls[url_name]}"
            )

        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user,
            slug=generate_unique_slug('Test Note')
        )
        for url_name in ['detail', 'edit', 'delete']:
            response = self.client.get(self.urls[url_name],
                                       kwargs={'slug': note.slug})
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response, f"/auth/login/?next={self.urls[url_name]}"
            )
