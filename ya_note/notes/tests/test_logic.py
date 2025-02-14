from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pytils.translit import slugify

from notes.models import Note


class YaNoteLogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.add_url = reverse('notes:add')
        self.other_user = User.objects.create_user(username='otheruser',
                                                   password='otherpass123')
        self.note = Note.objects.create(title='Note for Editing',
                                        text='Content for Editing',
                                        author=self.user)
        self.other_note = Note.objects.create(
            title='Note for Editing by Other',
            text='Content for Editing by Other',
            author=self.other_user
        )

    def test_logged_in_user_can_create_note(self):
        note_count = Note.objects.count()
        response = self.client.post(
            self.add_url,
            {
                'title': 'Test Note',
                'text': 'Test Content'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), note_count + 1)
        last_note = Note.objects.last()
        self.assertEqual(last_note.title, 'Test Note')
        self.assertEqual(last_note.text, 'Test Content')
        self.assertEqual(last_note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        data = {
            'title': 'Test Note',
            'text': 'Test Content'
        }
        self.client.logout()
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(title='Test Note').exists())

    def test_unique_slug(self):
        Note.objects.create(
            title='Note 1',
            text='Content 1',
            author=self.user,
            slug='unique-slug'
        )
        with self.assertRaises(Exception):
            Note.objects.create(
                title='Note 2',
                text='Content 2',
                author=self.user,
                slug='unique-slug'
            )

    def test_view_creates_unique_slug(self):
        response = self.client.post(
            reverse('notes:add'),
            {
                'title': 'Note with Unique Slug',
                'text': 'Content for Unique Slug'
            }
        )
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title='Note with Unique Slug')
        self.assertTrue(Note.objects.filter(slug=note.slug).exists())

        response = self.client.post(
            reverse('notes:add'),
            {
                'title': 'Another Note',
                'text': 'Content for Another Note',
                'slug': note.slug
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('slug', response.context['form'].errors)
        self.assertFalse(Note.objects.filter(title='Another Note').exists())

    def test_automatic_slug_generation(self):
        url = reverse('notes:add')
        data = {
            'title': 'Test Note without Slug',
            'text': 'Test Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        note = Note.objects.filter(title='Test Note without Slug').last()
        self.assertEqual(note.slug, slugify(note.title))

    def test_user_can_edit_own_note(self):
        new_title = 'Updated Note'
        new_text = 'Updated Content'
        url = reverse('notes:edit', args=[self.note.slug])
        data = {
            'title': new_title,
            'text': new_text
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_title)
        self.assertEqual(self.note.text, new_text)
        self.assertEqual(self.note.author, self.user)

    def test_user_can_delete_own_note(self):
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cannot_edit_others_note(self):
        new_title = 'Updated Note'
        new_text = 'Updated Content'
        url = reverse('notes:edit', args=(self.other_note.slug,))
        data = {
            'title': new_title,
            'text': new_text
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
        self.other_note.refresh_from_db()
        self.assertNotEqual(self.other_note.title, new_title)
        self.assertNotEqual(self.other_note.text, new_text)

    def test_user_cannot_delete_others_note(self):
        delete_url = reverse('notes:delete', args=(self.other_note.slug,))
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(pk=self.other_note.pk).exists())
