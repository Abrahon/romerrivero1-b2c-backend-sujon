from django.apps import AppConfig

class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2b.order'

    def ready(self):
        import b2b.order.signals
