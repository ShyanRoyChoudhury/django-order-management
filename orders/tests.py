from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from orders.models import Order, Status


class OrdersViewsTests(APITestCase):
    def register_and_login(self, name='Test User', email='test@example.com', password='StrongPass123!'):
        register_url = reverse('register_user')
        self.client.post(register_url, {
            'name': name,
            'email': email,
            'password': password
        }, format='json')
        login_url = reverse('login_user')
        resp = self.client.post(login_url, {
            'email': email,
            'password': password
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token

    def test_create_order_success(self):
        self.register_and_login()
        url = reverse('orders_handler')
        payload = {
            'product_name': 'Widget',
            'quantity': 2,
            'amount': '19.99'
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_id', resp.data)
        uid = resp.data['order_id']
        self.assertTrue(Order.objects.filter(uid=uid).exists())

    def test_list_orders_pagination(self):
        self.register_and_login()
        create_url = reverse('orders_handler')
        for i in range(12):
            self.client.post(create_url, {
                'product_name': f'Item {i}',
                'quantity': 1,
                'amount': '5.00'
            }, format='json')

        list_url = reverse('orders_handler')
        resp_page1 = self.client.get(list_url)
        self.assertEqual(resp_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_page1.data.get('count'), 12)
        self.assertEqual(len(resp_page1.data.get('results')), 10)
        self.assertIsNotNone(resp_page1.data.get('next'))
        self.assertIsNone(resp_page1.data.get('previous'))

        resp_page2 = self.client.get(f"{list_url}?page=2")
        self.assertEqual(resp_page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_page2.data.get('results')), 2)

    def test_cancel_order_success(self):
        self.register_and_login()
        create_resp = self.client.post(reverse('orders_handler'), {
            'product_name': 'Gadget',
            'quantity': 1,
            'amount': '9.99'
        }, format='json')
        uid = create_resp.data['order_id']
        cancel_url = reverse('cancel_order', kwargs={'order_id': uid})
        cancel_resp = self.client.patch(cancel_url)
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(uid=uid)
        self.assertEqual(order.status, Status.CANCELLED)

    def test_cancel_order_not_found(self):
        self.register_and_login()
        cancel_url = reverse('cancel_order', kwargs={'order_id': 'non-existent-uid'})
        resp = self.client.patch(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', resp.data)
