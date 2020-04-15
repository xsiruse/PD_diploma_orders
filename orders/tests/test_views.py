# import json
# from rest_framework import status
# from django.test import TestCase, Client
import os

from django.urls import reverse
# from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
#     ConfirmEmailToken, Contact, User
# from orders.serializers import UserSerializer, ProductInfoSerializer, CategorySerializer, ShopSerializer, \
#     ProductSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer
from rest_framework.test import APIRequestFactory



# def hide():
#     # # initialize the APIClient app
#     # client = Client()
#     #
#     #
#     # class GetSingleProductInfoTest(TestCase):
#     #     """ Test module for GET single ProductInfo API """
#     #
#     #     def setUp(self):
#     #         self.test_cat = Category.objects.create(
#     #             name='test_cat',
#     #             pk='999'
#     #         )
#     #         self.test_prod = Product.objects.create(
#     #             name='test_prod',
#     #             category='999',
#     #             pk='999'
#     #         )
#     #         self.test_prodinfo = ProductInfo.objects.create(
#     #             name='test_prodinfo',
#     #             shop='2',
#     #             product='999',
#     #             quantity="999",
#     #             price='999',
#     #             price_rrc='999')
#     #         self.test_cat1 = Category.objects.create(
#     #             name='test_cat1',
#     #             pk='998'
#     #         )
#     #         self.test_prod1 = Product.objects.create(
#     #             name='test_prod1',
#     #             category='998',
#     #             pk='998'
#     #         )
#     #         self.test_prodinfo1 = ProductInfo.objects.create(
#     #             name='test_prodinfo1',
#     #             shop='2',
#     #             product='998',
#     #             quantity="999",
#     #             price='999',
#     #             price_rrc='999')
#     #
#     #
#     #     def test_get_valid_single_prodinfo(self):
#     #         response = client.get(
#     #             reverse('product-details', kwargs={'pk': self.test_prodinfo1.pk}))
#     #         product = ProductInfo.objects.get(pk=self.test_prodinfo1.pk)
#     #         serializer = ProductInfoSerializer(product)
#     #         self.assertEqual(response.data, serializer.data)
#     #         self.assertEqual(response.status_code, status.HTTP_200_OK)
#     #
#     #     def test_get_invalid_single_prodinfo(self):
#     #         response = client.get(
#     #             reverse('product-details', kwargs={'pk': 30}))
#     #         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#     return
#
# fixt_shop = os.path()
#
# # Using the standard RequestFactory API to create a form POST request
# # factory = APIRequestFactory()
# # request = factory.post(reverse('partner-update'), {'url': })
