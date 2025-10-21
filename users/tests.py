from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser


class UsersViewsTests(APITestCase):
    def test_register_user_success(self):
        url = reverse('register_user')
        payload = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'password': 'StrongPass123!'
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data.get('message'), 'User registered')
        self.assertTrue(CustomUser.objects.filter(email='alice@example.com').exists())

    def test_register_user_conflict_email(self):
        url = reverse('register_user')
        payload = {
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': 'StrongPass123!'
        }
        first = self.client.post(url, payload, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(url, payload, format='json')
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('errors', second.data)

    def test_login_user_success(self):
        register_url = reverse('register_user')
        self.client.post(register_url, {
            'name': 'Charlie',
            'email': 'charlie@example.com',
            'password': 'StrongPass123!'
        }, format='json')

        login_url = reverse('login_user')
        resp = self.client.post(login_url, {
            'email': 'charlie@example.com',
            'password': 'StrongPass123!'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('message'), 'Login successful')
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_user_invalid_password(self):
        register_url = reverse('register_user')
        self.client.post(register_url, {
            'name': 'Dana',
            'email': 'dana@example.com',
            'password': 'StrongPass123!'
        }, format='json')

        login_url = reverse('login_user')
        resp = self.client.post(login_url, {
            'email': 'dana@example.com',
            'password': 'WrongPassword!'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('errors', resp.data)
