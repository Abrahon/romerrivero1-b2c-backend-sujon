from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2c.payments'

    def ready(self):
        import b2c.payments.signals
    