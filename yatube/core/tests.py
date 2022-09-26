from ctypes import addressof
from re import template
from django.test import TestCase, Client
from django.urls import reverse


class TestErrorsUrl(TestCase):
    def setUp(self):
        self.cleint = Client()

    def test_404_and_403_urls(self):
        check_list = [
            ('core/404.html', '/smth/idk/'),
            # ('core/403csrf.html', '???') не знаю какую ссылку
        ]
        for tuple in check_list:
            template, address = tuple
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
