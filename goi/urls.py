from django.urls import path
from . import views
from goi.admin import goi_admin_site
urlpatterns =[

    path('', views.index, name ='index'),
    path('course/',views.course,name='course'),
    path('lecture/',views.lecture,name='lecture'),
    path('update/',views.update,name='update'),
    path('updatepage/',views.updatepage,name='updatepage'),
    path('volunteer/',views.volunteer,name='volunteer'),
    path('goi-admin/', goi_admin_site.urls),
]