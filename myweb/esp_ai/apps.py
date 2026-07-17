from django.apps import AppConfig

class EspAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # QUAN TRỌNG: Phải có tiền tố myweb. ở đây
    name = 'myweb.esp_ai'