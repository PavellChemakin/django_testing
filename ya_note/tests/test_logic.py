import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from ya_note.notes.models import Note

from pytils.translit import slugify


class YaNoteLogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass123')
        self.client = Client()

    def test_logged_in_user_can_create_note(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('notes:create'),
            {
                'title': 'Test Note',
                'content': 'Test Content'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='Test Note').exists())

    def test_anonymous_user_cannot_create_note(self):
        url = reverse('notes:create')
        data = {
            'title': 'Test Note',
            'content': 'Test Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(title='Test Note').exists())

    def test_unique_slug(self):
        Note.objects.create(
            title='Note 1',
            content='Content 1',
            user=self.user,
            slug='unique-slug'
        )
        with self.assertRaises(Exception):
            Note.objects.create(
                title='Note 2',
                content='Content 2',
                user=self.user,
                slug='unique-slug'
            )

    def test_automatic_slug_generation(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('notes:create')
        data = {
            'title': 'Test Note without Slug',
            'content': 'Test Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title='Test Note without Slug')
        self.assertEqual(note.slug, slugify(note.title))

    def test_user_can_edit_and_delete_own_notes(self):
        note = Note.objects.create(title='Note for Editing',
                                   content='Content for Editing',
                                   user=self.user)
        self.client.login(username='testuser', password='testpass123')

        url = reverse('notes:update', args=[note.slug])
        data = {
            'title': 'Updated Note',
            'content': 'Updated Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Note')

        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())

    def test_user_cannot_edit_or_delete_others_notes(self):
        other_user = User.objects.create_user(username='otheruser',
                                              password='otherpass123')
        note = Note.objects.create(title='Note for Editing',
                                   content='Content for Editing',
                                   user=other_user)
        self.client.login(username='testuser', password='testpass123')

        url = reverse('notes:update', args=[note.slug])
        data = {
            'title': 'Updated Note',
            'content': 'Updated Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
        note.refresh_from_db()
        self.assertNotEqual(note.title, 'Updated Note')

        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(pk=note.pk).exists())


if __name__ == '__main__':
    unittest.main()
