from http import HTTPStatus

from django.test import Client, TestCase


class CoreUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_404(self):
        response = CoreUrlsTest.guest_client.get('/core/тест/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
