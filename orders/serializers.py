from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer, IntegerField

from orders.models import Shop, Product, ProductParameter, ProductInfo, Category, User, OrderItem, Order


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category',)
        extra_kwargs = {'name': {'required': False}}


class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'name', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class ParameterSerializer(ModelSerializer):
    pass


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = IntegerField()
    contact = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'status', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)


class ContactSerializer(ModelSerializer):
    pass
