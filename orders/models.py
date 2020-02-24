from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

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


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()  ## This is the new line in the User model. ##

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)


class Shop(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    url = models.URLField(verbose_name="Ссылка", null=True, blank=True)
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)
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
        return f'%s для %s = %s' % (self.parameter, self.product_info, self.value)


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
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items',
                              on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позтция заказа'
        verbose_name_plural = 'Позтции в заказе'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]


class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'

