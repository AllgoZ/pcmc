"""
URL configuration for pcmc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from pcmc_app.views import home
from django.conf import settings
from django.conf.urls.static import static
from hp.admin import hp_admin_site
from goi.admin import goi_admin_site
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('pcmc_app.urls') ),
    path('home/',home,name='home'),
    path('', include('goi.urls')),
    path('goi/', include('goi.urls')),
    #path('hp/',include('hp.urls')),
    path('hp-admin/', hp_admin_site.urls),
    path('goi-admin/', goi_admin_site.urls),

]

urlpatterns=urlpatterns+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
