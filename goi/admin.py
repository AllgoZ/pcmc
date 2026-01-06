from django.contrib.admin import AdminSite
from .models import Volunteer
class GOI(AdminSite):
    site_header = "GOI Admin"
    site_title = "goi Admin Portal"
    index_title = "Welcome to Goi Admin"

goi_admin_site = GOI(name='goi_admin')
# Register your models here.
goi_admin_site.register(Volunteer)