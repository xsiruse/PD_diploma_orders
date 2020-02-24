from django.core.mail import EmailMultiAlternatives
from django.dispatch import Signal, receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from main import settings
from orders.models import ConfirmEmailToken, User

new_user_registered = Signal(
    providing_args=['user_id'],
)

new_order = Signal(
    providing_args=['user_id'],
)


@receiver(reset_password_token_created)
def password_reset_token_created_signal(sender, instance, reset_password_token, **kwargs):
    """
    Уведомление об успешном подтверждении регистрации
    """
    # send an e-mail to the user

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset successful for {reset_password_token.user}",
        # message:
        f'Password Reset successful for {reset_password_token.user}',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.send()


@receiver(new_user_registered)
def new_user_registered_signal(user_id, sender, url, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    print('signal %s cought' % sender.__name__)
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()
