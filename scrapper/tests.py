import json

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse


class ScrapperTestCase(TestCase):
    def test_search_view(self):
        response = self.client.post(reverse('search'), {'molecules': 'ozone'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('data_list', self.client.session)

    def test_download_file_views(self):
        response_pdf = self.client.post(reverse('download_file'), {'download_type': 'pdf'})
        response_json = self.client.post(reverse('download_file'), {'download_type': 'json'})

        self.assertEqual(response_pdf.status_code, 200)
        self.assertEqual(response_json.status_code, 200)

        self.assertIsInstance(response_pdf, HttpResponse)
        self.assertIn(b'%PDF', response_pdf.content)

        self.assertIsInstance(response_json, HttpResponse)
        try:
            json.loads(response_json.content)
        except json.JSONDecodeError:
            self.fail("O conteúdo não é um JSON válido.")

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

