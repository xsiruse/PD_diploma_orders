from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User
from orders.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact


@register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


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
