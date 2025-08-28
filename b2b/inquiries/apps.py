from django.apps import AppConfig

class InquiriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b2b.inquiries'

    def ready(self):
        import b2b.inquiries.signals
