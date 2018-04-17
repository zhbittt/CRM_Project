from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'



#在每个应用里的app.py下，添加ready
# from django.utils.module_loading import autodiscover_modules
# class CrmConfig(AppConfig):
#     name = 'crm'
#
#     def ready(self):
#         autodiscover_modules("stark")