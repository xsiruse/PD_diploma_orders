from django.contrib.admin import register, ModelAdmin

from orders.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact


@register(Shop)
class ShopAdmin(ModelAdmin):
    Shop._meta.verbose_name_plural = "Магазины ( %s ) " % Shop.objects.all().count()


@register(Category)
class CategoryAdmin(ModelAdmin):
    Category._meta.verbose_name_plural = "Категории ( %s ) " % Category.objects.all().count()


@register(Product)
class ProductAdmin(ModelAdmin):
    Product._meta.verbose_name_plural = "Продукты ( %s ) " % Product.objects.all().count()


@register(ProductInfo)
class ProductInfoAdmin(ModelAdmin):
    ProductInfo._meta.verbose_name_plural = "Информация о продуктах ( %s ) " % ProductInfo.objects.all().count()


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    Parameter._meta.verbose_name_plural = "Параметры ( %s ) " % Parameter.objects.all().count()


@register(ProductParameter)
class ProductParameterAdmin(ModelAdmin):
    ProductParameter._meta.verbose_name_plural = "Параметры продуктов ( %s ) " % ProductParameter.objects.all().count()


@register(Order)
class OrderAdmin(ModelAdmin):
    Order._meta.verbose_name_plural = "Заказы ( %s ) " % Order.objects.all().count()


@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
   OrderItem._meta.verbose_name_plural = "Единицы заказов ( %s ) " % OrderItem.objects.all().count()


@register(Contact)
class ContactAdmin(ModelAdmin):
    Contact._meta.verbose_name_plural = "Контакты ( %s ) " % Contact.objects.all().count()
