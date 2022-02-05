from django.test import Client, TestCase
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_available_for_unauthorised_user(self):
        """Проверяем доступность страниц about неавторизованному
        пользователю."""
        urls_available_for_all = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for url, expected in urls_available_for_all.items():
            response = self.guest_client.get(url)
            with self.subTest(value=response):
                self.assertEqual(response.status_code, expected)
