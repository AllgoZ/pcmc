from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import ProductDetails, HpPersonaldetails, Location, BrandingImage,Order


class HpAdminSite(AdminSite):
    site_header = "HP Admin"
    site_title = "HP Admin Portal"
    index_title = "Welcome to HP Admin"

hp_admin_site = HpAdminSite(name='hp_admin')

# Register hp models with hp_admin_site
hp_admin_site.register(ProductDetails)
hp_admin_site.register(HpPersonaldetails)
hp_admin_site.register(Location)
hp_admin_site.register(BrandingImage)
hp_admin_site.register(Order)

