"""CRM_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from stark.service import v1
from crm import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^stark/', v1.site.urls),
    url(r'^eee/', views.eee),
    url(r'^login/', views.login),
    url(r'^get_validCode_img/', views.get_validCode_img),
    url(r'^index/', views.index),
    url(r'^monthcount/', views.month_single_count),
    url(r'^monthrate/', views.month_single_rate),
    url(r'^monthuser/', views.month_user_count),

]
