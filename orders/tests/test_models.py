import fake as fake
from django.test import TestCase

from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category, Order, OrderItem, \
    ConfirmEmailToken, Contact, User


class ProductModelTest(TestCase):
    def setUp(self):
        Product.objects.create(
            name=fake.name(),
            category=fake.category()
        )

    def test_save_model(self):
        saved_models = Product.objects.count()
        self.assertEqual(saved_models, 2)
