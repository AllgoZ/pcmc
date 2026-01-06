from django.db import models
from django.utils import timezone
class UserProfile(models.Model):
    user_id = models.CharField(max_length=100, unique=True)  # to store unique user IDs
    password = models.CharField(max_length=100)  # store passwords (hashed in production)
    name = models.CharField(max_length=100)  # to store user's name

    def __str__(self):
        return self.user_id
    

class HpPersonaldetails(models.Model):
    district = models.CharField(max_length=50)
    other_district = models.CharField(max_length=50, blank=True, null=True)
    town = models.CharField(max_length=50)
    other_town = models.CharField(max_length=50, blank=True, null=True)
    outlet_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()

    # Use CharFields for fields that use checkboxes in the HTML
    pragati_app_enrolled = models.CharField(max_length=20, choices=[('Yes', 'Yes'), ('No', 'No'), ('Already Enrolled', 'Already Enrolled')],default='Not Specified')
    existing_hpcl_customer = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')],default='Not Specified')
    
    branding_flanges = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')],default='Not Specified')
    branding_danglers = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')],default='Not Specified')
    #delivery = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')],default='Not Specified')

    most_sold_lube = models.CharField(max_length=255)

    # For multiple options in checkboxes like 2-wheeler, 4-wheeler, and Heavy Vehicle
    application_of_lube = models.CharField(max_length=50,default='Not Specified')
    created_by = models.CharField(max_length=100, default='system')  # Optional, stores who created the record
    created_date = models.CharField(max_length=100, default=timezone.now().strftime('%Y-%m-%d %H:%M:%S'))  # Store as string in 'YYYY-MM-DD HH:MM:SS' formatd
    sync_date = models.DateTimeField(auto_now=True)  # Automatically updates to the current time whenever the object is saved
    
    # Additional field for tracking user (as specified in your requirements)
    retailer_id = models.CharField(max_length=10, unique=True, default="00_100")
    
    '''def save(self, *args, **kwargs):
        # Auto-increment retailer_id starting from 100
        if not self.retailer_id:
            last_retailer = HpPersonaldetails.objects.all().order_by('retailer_id').last()
            self.retailer_id = last_retailer.retailer_id + 1 if last_retailer else 100
        super(HpPersonaldetails, self).save(*args, **kwargs)'''

    def __str__(self):
        return f"{self.outlet_name} - {self.retailer_id}"
    class Meta:
        app_label = 'hp' 
        db_table = 'hp_personaldetails'


class ProductDetails(models.Model):
    CATEGORY_CHOICES = [
        ('mco', 'Motorcycle Oil'),  # MCO: Motorcycle Oil
        ('deo', 'Diesel Engine Oil'),  # DEO: Diesel Engine Oil
        ('pco', 'Passenger Car Oil'),  # PCO: Passenger Car Oil
    ]

    name = models.CharField(max_length=100)  # Product name, e.g., NEOSYNTH
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  # Category with updated choices
    image = models.ImageField(upload_to='products/')  # Path to product image
    applications = models.TextField()  # Application details text
    features = models.TextField()  # List or description of features and benefits
    quantities = models.JSONField(default=list)  # List of quantities in different sizes (e.g., [{'size': '650ml', 'quantity': 100}, ...])

    def __str__(self):
        return f"{self.name} - {self.category}"


class Location(models.Model):
    region = models.CharField(max_length=100,default='Ahe')  # Non-nullable field, must be filled for all rows
    district = models.CharField(max_length=100,blank=True)  # Non-nullable field, must be filled for all rows
    town = models.CharField(max_length=100,blank=True)  # Nullable field

    def __str__(self):
        return f"{self.region} - {self.district} - {self.town}"


class BrandingImage(models.Model):
    # Choices for different branding image categories
    IMAGE_CATEGORIES = [
        ('complete_shop', 'Complete Shop Photo'),
        ('dealer_board', 'Dealer Board Close shot'),
        ('inside_wall', 'Inside Wall'),
        ('flanges', 'Flanges'),
        ('dangler', 'Dangler'),
        ('interaction', 'Interaction'),
        ('others', 'Others'),
    ]

    category = models.CharField(
        max_length=50,
        choices=IMAGE_CATEGORIES,
        default='others',
    )
    
    # Image field to store the uploaded image
    image = models.ImageField(upload_to='branding_images/')
    # Optional: Timestamp when the image was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)
    retailer_id = models.CharField(max_length=10,default="unknown")
    def __str__(self):
        return f"{self.get_category_display()} - {self.uploaded_at}"
    



class Order(models.Model):
    delivery = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='Not Specified')
    interested_in_futur_x = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='Not Specified')
    retailer_id = models.CharField(max_length=10, default="unknown")
    product = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=50,default="1L")  # Added SKU field
    timestamp = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"Order by {self.retailer_id} - {self.product} x {self.quantity}"

class Item(models.Model):
    name = models.CharField(max_length=255)  # Item name
    description = models.TextField()  # Item description
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of last update

    def __str__(self):
        return self.name