from django.urls import path,include
from . import views
from .views import ItemViewSet
from rest_framework.routers import DefaultRouter
from .views import (
    HpPersonaldetailsUpdateView,
    BrandingImageUpdateView,
    OrderUpdateView,
    LoginApiView,
)
router = DefaultRouter()
router.register(r'items', ItemViewSet)  # This will automatically create the appropriate routes

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.index, name='index'),  # URL for index.html
    path('selection/', views.selection, name='selection'),  # URL for selection.html
    path('catalog/', views.catalog, name='catalog'),  # URL for catalog.html
    path('dashboard/', views.dashboard, name='dashboard'),  # URL for dashboard.html
    path('personaldetails/', views.personaldetails, name='personaldetails'),  # URL for personaldetails.html
    path('thankyou/', views.thankyou, name='thankyou'),  # URL for thankyou.html
    path('upload/', views.upload, name='upload'),  # URL for upload.html
    path('quiz/',views.quiz,name='quiz'),
    path('api/hppersonaldetails/', HpPersonaldetailsUpdateView.as_view(), name='hppersonaldetails'),
    path('api/brandingimage/', BrandingImageUpdateView.as_view(), name='brandingimage'),
    path('api/order/', OrderUpdateView.as_view(), name='order'),
    path('api/login/', LoginApiView.as_view(), name='login_api'),
    
]
