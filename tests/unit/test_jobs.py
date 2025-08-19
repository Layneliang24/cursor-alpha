from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


class JobsPlaceholderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='u1', password='p1', email='u1@example.com')
        self.client.force_authenticate(self.user)

    def test_jobs_list(self):
        resp = self.client.get('/api/v1/jobs/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('success'))

