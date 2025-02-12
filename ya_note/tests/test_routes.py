import unittest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ya_note.notes.models import Note


class RouteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.client.force_login(self.user)

    def test_home_page_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_pages(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('notes:create'))
        self.assertEqual(response.status_code, 200)

    def test_note_detail_update_delete_pages(self):
        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user
        )
        response = self.client.get(reverse('notes:detail', args=[note.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('notes:update', args=[note.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 200)

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
        self.client.force_login(other_user)
        response = self.client.get(reverse('notes:detail', args=[note.slug]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('notes:update', args=[note.slug]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('notes:list')}")

        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('notes:success')}")
        response = self.client.get(reverse('notes:create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('notes:create')}")

        note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.user
        )
        response = self.client.get(reverse('notes:detail', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        detail_url = reverse('notes:detail', args=[note.slug])
        self.assertRedirects(response, f"{login_url}?next={detail_url}")

        response = self.client.get(reverse('notes:update', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        update_url = reverse('notes:update', args=note.slug)
        self.assertRedirects(response, f"{login_url}?next={update_url}")

        response = self.client.get(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        delete_url = reverse('notes:delete', args=note.slug)
        self.assertRedirects(response, f"{login_url}?next={delete_url}")

    def test_public_pages_available_to_all(self):
        self.client.logout()

        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user)

        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
