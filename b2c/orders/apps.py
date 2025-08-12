from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2c.orders'

    def ready(self):
        import  b2c.orders.signals 

