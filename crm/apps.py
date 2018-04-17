from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class CrmConfig(AppConfig):
    name = 'crm'
    def ready(self):
        autodiscover_modules("stark")


