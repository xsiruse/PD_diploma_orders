
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
    ConfirmEmailToken, Contact, User


class UserRegisterTest(APITestCase):

    def setUp(self):
        self.email = 'test@test.test'
        # urls = 'orders.api_urls'

    def test_register_user(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse_lazy('orders:user-register')
        data = {'first_name': 'test',
                'last_name': 'test',
                'email': self.email,
                'password': 'test',
                'company': 'test',
                'position': 'test', }
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(User.objects.filter(email=self.email))
        self.assertEqual(User.objects.filter(email=self.email).only('last_name'), 'test')

    def test_register_user_Confirm(self):
        """
        Ensure we can create a new account object.
        """
        token = ConfirmEmailToken.objects.filter(user__email=self.email).only('key')
        url = reverse_lazy('orders:user-register-confirm')
        data = {'email': self.email,
                'token': token, }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(email=self.email).only('is_active'), 1)
