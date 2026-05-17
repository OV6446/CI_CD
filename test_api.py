"""Тесты основных HTTP-эндпоинтов приложения."""
import os
import unittest

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertIn(response.status_code, (200, 302))

    def test_register_page(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.client.get('/search/')
        self.assertIn(response.status_code, (200, 302))

    def test_radio_page(self):
        response = self.client.get('/radio/')
        self.assertIn(response.status_code, (200, 302))


if __name__ == '__main__':
    unittest.main()
