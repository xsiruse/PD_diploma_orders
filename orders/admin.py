from django.contrib.admin import register, ModelAdmin

from orders.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact


@register(Shop)
class ShopAdmin(ModelAdmin):
    pass


@register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@register(Product)
class ProductAdmin(ModelAdmin):
    pass


@register(ProductInfo)
class ProductInfoAdmin(ModelAdmin):
    pass


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    pass


@register(ProductParameter)
class ProductParameterAdmin(ModelAdmin):
    pass


@register(Order)
class OrderAdmin(ModelAdmin):
    pass


@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    pass


@register(Contact)
class ContactAdmin(ModelAdmin):
    pass
