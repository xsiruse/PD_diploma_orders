from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
    ConfirmEmailToken, Contact, User


class UserRegisterTest(APITestCase):

    def setUp(self):
        self.email = 'test@test.test'
        # urls = 'orders.api_urls'
        self.data = {'first_name': 'test',
                     'last_name': 'test',
                     'email': self.email,
                     'password': 'QWErty123$',
                     'company': 'test',
                     'position': 'test',
                     }

    def test_register_user(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse_lazy('orders:user-register')

        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().last_name, self.data['last_name'])

    def test_register_user_Confirm(self):
        """
        Ensure we can create a new account object.
        """
        # print(**self.data)
        url = reverse_lazy('orders:user-register-confirm')
        user = User.objects.create_user(self.data['email'], self.data['password'])
        ConfirmEmailToken.objects.create(user_id=user.id, key=456)
        token = ConfirmEmailToken.objects.get().key
        # print(User.objects.all())
        # print(token)
        data = {'email': self.email,
                'token': token, }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().is_active, 1)
