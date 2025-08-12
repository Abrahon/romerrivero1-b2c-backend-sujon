from django.apps import AppConfig


class AddProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2c.admin.add_product'
    
    def ready(self):
        import b2c.admin.add_product.signals 
