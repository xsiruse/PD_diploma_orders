from django.contrib.auth.models import AbstractUser
from django.db import models

STATE_CHOICES = (
    ('basket', 'Статус корзины...'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)


class User(AbstractUser):
    pass


class Shop(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    url = models.URLField(verbose_name="Ссылка", null=True, blank=True)
    # filename = models.FilePathField(verbose_name="Имя файла")

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категрия'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    shop = models.ForeignKey(Shop, verbose_name='Магазин',
                             related_name='prod_info_shop',
                             on_delete=models.CASCADE,
                             blank=True)
    product = models.ForeignKey(Product,
                                verbose_name='для продукта',
                                related_name='product_infos',
                                blank=True,
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Перечень информации о продукте'

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameters',
                                     on_delete=models.CASCADE,
                                     blank=True)
    parameter = models.ForeignKey(Parameter,
                                  verbose_name='Параметр',
                                  related_name='product_parameters',
                                  on_delete=models.CASCADE,
                                  blank=True)
    value = models.CharField(verbose_name='Значение',
                             max_length=100,
                             blank=True)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Перечень параметров продукта'

    def __str__(self):
        return self.parameter


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позтция заказа'
        verbose_name_plural = 'Позтции в заказе'


class Contact(models.Model):
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name="Значение")

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return self.value
