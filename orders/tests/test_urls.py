from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
    ConfirmEmailToken, Contact, User


class UserRegisterTest(APITestCase):

    def __init__(self):
        self.email = 'test@test.test'

    def test_register_user(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('user-register')
        data = {'first_name': 'test',
                'last_name': 'test',
                'email': self.email,
                'password': 'test',
                'company': 'test',
                'position': 'test', }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().last_name, 'test')

    def test_register_user_Confirm(self):
        """
        Ensure we can create a new account object.
        """
        token = ConfirmEmailToken.objects.filter(user__email='test@test.test').key()
        url = reverse('user-register-confirm')
        data = {'email': self.email,
                'token': token, }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(email=self.email).is_active(), 1)
