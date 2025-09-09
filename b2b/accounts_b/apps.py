from django.apps import AppConfig

class AccountsBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2b.accounts_b'

    def ready(self):
        
        import b2b.accounts_b.signals
