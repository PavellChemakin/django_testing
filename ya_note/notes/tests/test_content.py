import unittest
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from notes.models import Note


class YaNoteContentTests(TestCase):
    def setUp(self):
        self.user_one = User.objects.create_user(username='user1',
                                                 password='testpass123')
        self.user_two = User.objects.create_user(username='user2',
                                                 password='testpass123')

        self.note_by_user_one = Note.objects.create(title='Note 1',
                                                    text='Content 1',
                                                    author=self.user_one)
        self.note_by_user_two = Note.objects.create(title='Note 2',
                                                    text='Content 2',
                                                    author=self.user_two)

        self.client.login(username='user1', password='testpass123')

        self.list_url = reverse('notes:list')
        self.add_url = reverse('notes:add')
        self.edit_url = reverse('notes:edit',
                                args=[self.note_by_user_one.slug])

    def test_note_in_object_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('object_list' in response.context)
        object_list = response.context['object_list']
        self.assertTrue(self.note_by_user_one in object_list)
        object_list = response.context['object_list']
        self.assertFalse(self.note_by_user_two in object_list)

    def test_user_sees_only_own_notes(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        self.assertTrue(self.note_by_user_one in object_list)
        object_list = response.context['object_list']
        self.assertFalse(self.note_by_user_two in object_list)

    def test_form_on_create_page(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('form' in response.context)

    def test_form_on_update_page(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('form' in response.context)
