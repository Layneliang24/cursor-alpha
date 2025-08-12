from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        resp = self.client.get('/api/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ok', resp.data)
        self.assertIn('details', resp.data)


class ApiRootTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_root(self):
        resp = self.client.get('/api/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('status'), 'running')

# Create your tests here.
