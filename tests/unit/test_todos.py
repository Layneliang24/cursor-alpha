from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


class TodosPlaceholderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='u2', password='p2', email='u2@example.com')
        self.client.force_authenticate(self.user)

    def test_todos_list(self):
        resp = self.client.get('/api/v1/todos/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('success'))

