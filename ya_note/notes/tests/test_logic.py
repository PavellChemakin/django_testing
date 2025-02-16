from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pytils.translit import slugify

from notes.models import Note


class YaNoteLogicTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.add_url = reverse('notes:add')

        self.other_username = 'otheruser'
        self.other_password = 'otherpass123'
        self.other_user = User.objects.create_user(
            username=self.other_username, password=self.other_password)

        self.note_title = 'Note for Editing'
        self.note_text = 'Content for Editing'
        self.note = Note.objects.create(title=self.note_title,
                                        text=self.note_text, author=self.user)

        self.other_note_title = 'Note for Editing by Other'
        self.other_note_text = 'Content for Editing by Other'
        self.other_note = Note.objects.create(
            title=self.other_note_title,
            text=self.other_note_text,
            author=self.other_user)

    def test_logged_in_user_can_create_note(self):
        note_count = Note.objects.count()
        new_note_title = 'Test Note'
        new_note_text = 'Test Content'
        response = self.client.post(
            self.add_url,
            {
                'title': new_note_title,
                'text': new_note_text
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), note_count + 1)
        last_note = Note.objects.last()
        self.assertEqual(last_note.title, new_note_title)
        self.assertEqual(last_note.text, new_note_text)
        self.assertEqual(last_note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        title = 'Test Note'
        text = 'Test Content'
        data = {
            'title': title,
            'text': text
        }
        self.client.logout()
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        login_url = reverse('login')
        self.assertRedirects(response, f"{login_url}?next={self.add_url}")
        self.assertFalse(Note.objects.filter(title=title).exists())
        self.assertFalse(Note.objects.filter(text=text).exists())

    def test_unique_slug(self):
        unique_slug_base = 'unique-slug'
        unique_slug = slugify(unique_slug_base)
        title1 = 'Note 1'
        text1 = 'Content 1'
        title2 = 'Note 2'
        text2 = 'Content 2'
        Note.objects.create(
            title=title1,
            text=text1,
            author=self.user,
            slug=unique_slug
        )
        with self.assertRaises(Exception):
            Note.objects.create(
                title=title2,
                text=text2,
                author=self.user,
                slug=unique_slug
            )

    def test_view_creates_unique_slug(self):
        unique_title = 'Note with Unique Slug'
        unique_content = 'Content for Unique Slug'
        another_title = 'Another Note'
        another_content = 'Content for Another Note'
        response = self.client.post(
            reverse('notes:add'),
            {
                'title': unique_title,
                'text': unique_content
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.filter(title=unique_title).last()
        self.assertTrue(Note.objects.filter(slug=note.slug).exists())
        self.assertEqual(note.title, unique_title)
        self.assertEqual(note.text, unique_content)
        self.assertEqual(note.author, self.user)

        response = self.client.post(
            reverse('notes:add'),
            {
                'title': another_title,
                'text': another_content,
                'slug': note.slug
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertFalse(Note.objects.filter(title=another_title).exists())
        queryset = Note.objects.filter(slug=note.slug)
        queryset = queryset.exclude(pk=note.pk)
        self.assertFalse(queryset.exists())

    def test_automatic_slug_generation(self):
        test_title = 'Test Note without Slug'
        test_content = 'Test Content'
        url = reverse('notes:add')
        data = {
            'title': test_title,
            'text': test_content
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.filter(title=test_title).last()
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
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_title)
        self.assertEqual(self.note.text, new_text)
        self.assertEqual(self.note.author, self.user)

    def test_user_can_delete_own_note(self):
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cannot_edit_others_note(self):
        new_title = 'Updated Note'
        new_text = 'Updated Content'
        url = reverse('notes:edit', args=[self.other_note.slug])
        data = {
            'title': new_title,
            'text': new_text
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.other_note.refresh_from_db()
        self.assertNotEqual(self.other_note.title, new_title)
        self.assertNotEqual(self.other_note.text, new_text)

    def test_user_cannot_delete_others_note(self):
        delete_url = reverse('notes:delete', args=[self.other_note.slug])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.other_note.pk).exists())
