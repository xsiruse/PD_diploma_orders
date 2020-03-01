from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email(*args):
    print(args)
    msg = EmailMultiAlternatives(args)
    msg.send()


@shared_task
def test(*args):
    print('test OK')

