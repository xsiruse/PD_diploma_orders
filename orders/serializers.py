from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from orders.models import Shop, Product, ProductParameter, ProductInfo, Category


class ShopSerializer(ModelSerializer):
    pass


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)
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


class OrderSerializer(ModelSerializer):
    pass


class OrderItemSerializer(ModelSerializer):
    pass


class ContactSerializer(ModelSerializer):
    pass
