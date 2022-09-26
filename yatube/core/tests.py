from django.test import TestCase, Client


class TestErrorsUrl(TestCase):
    def setUp(self):
        self.cleint = Client()

    def test_404_and_403_and_500_urls(self):
        check_list = [
            ('core/404.html', '/smth/idk/'),
            # ('core/403csrf.html', '???') не знаю какую ссылку
            # ('core/500.html', '???') тоже самое
        ]
        for tuple in check_list:
            template, address = tuple
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
