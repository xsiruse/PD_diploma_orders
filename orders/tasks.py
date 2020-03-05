from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from main.celery import app


@app.task
def send_email(*args):
    print(args)
    msg = EmailMultiAlternatives(args)
    msg.send()


@app.task
def test(*args):
    print('test OK')

