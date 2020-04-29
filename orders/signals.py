from django.core.mail import EmailMultiAlternatives
from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created

from main import settings
from orders.models import ConfirmEmailToken, User

from .tasks import send_email, test

new_user_registered = Signal(
    providing_args=['user_id'],
)

new_order = Signal(
    providing_args=['user_id'],
)

logged_in = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created_signal(sender, instance, reset_password_token, **kwargs):
    """
    Уведомление об успешном подтверждении регистрации
    """

    title = f"Password Reset successful for {reset_password_token.user}",
    # message:
    message = f'Password Reset successful for {reset_password_token.user}',
    # from:
    from_ = settings.EMAIL_HOST_USER,
    # to:
    to = [reset_password_token.user.email]

    send_email.delay(title, message, from_, to)


@receiver(new_user_registered)
def new_user_registered_signal(user_id, sender, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    print('signal %s cought' % sender.__name__)
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    #     # title:
    title = f"Password Reset Token for {token.user.email}"
    #     # message:
    message = token.key
    #     # from:
    from_ = settings.EMAIL_HOST_USER
    #     # to:
    to = [token.user.email]
    send_email.delay(title, message, from_, to)


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)


        # title:
    title = f"Обновление статуса заказа",
        # message:
    message = 'Заказ сформирован',
        # from:
    from_ = settings.EMAIL_HOST_USER,
        # to:
    to = [user.email]
    send_email.delay(title, message, from_, to)


@receiver(logged_in)
def logged_in_signal(user_id, **kwargs):
    print('start')
    test.delay()
