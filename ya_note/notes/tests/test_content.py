import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from notes.models import Note


class YaNoteContentTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpass123')
        self.user2 = User.objects.create_user(username='user2',
                                              password='testpass123')
        self.note1 = Note.objects.create(title='Note 1', text='Content 1',
                                         author=self.user1)
        self.note2 = Note.objects.create(title='Note 2', text='Content 2',
                                         author=self.user2)

        self.client = Client()
        self.client.login(username='user1', password='testpass123')

    def test_note_in_object_list(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('object_list' in response.context)
        self.assertTrue(self.note1 in response.context['object_list'])
        self.assertFalse(self.note2 in response.context['object_list'])

    def test_user_sees_only_own_notes(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.note1 in response.context['object_list'])
        self.assertFalse(self.note2 in response.context['object_list'])

    def test_forms_on_create_and_update_pages(self):
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        response = self.client.get(reverse('notes:edit',
                                           args=[self.note1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)


if __name__ == '__main__':
    unittest.main()
