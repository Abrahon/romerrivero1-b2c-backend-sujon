

from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'b2c.user_profile'

    def ready(self):
        # Import signals here, inside ready()
        import b2c.user_profile.signals

