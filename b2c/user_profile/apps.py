from django.apps import AppConfig

class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "b2c.user_profile"

    def ready(self):
        import b2c.user_profile.signals  # 👈 this ensures signals are registered
