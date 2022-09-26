from http import HTTPStatus

from django.test import TestCase, Client


class AboutURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()

    def test_static_url(self):
        urls_names = [
            '/about/tech/',
            '/about/author/',
        ]
        for url in urls_names:
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_temaplates(self):
        templates_urls_names = [
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        ]
        for tuple in templates_urls_names:
            address, template = tuple
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
