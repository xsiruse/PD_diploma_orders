from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'orders'
    verbose_name = 'Бэкенд для заказов'

    def ready(self):
        """
        импортируем сигналы
        """