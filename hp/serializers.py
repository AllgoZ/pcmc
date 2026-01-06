from rest_framework import serializers
from .models import (
    UserProfile,
    HpPersonaldetails,
    ProductDetails,
    Location,
    BrandingImage,
    Order,
    Item,
)

import base64
import uuid
from django.core.files.base import ContentFile



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class HpPersonaldetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HpPersonaldetails
        fields = '__all__'


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetails
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class BrandingImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()  # Handle image as a base64 string

    # Mapping for human-readable category names to database values
    CATEGORY_MAP = {
        'Complete Shop Photo': 'complete_shop',
        'Dealer Board Close shot': 'dealer_board',
        'Inside Wall': 'inside_wall',
        'Flanges': 'flanges',
        'Dangler': 'dangler',
        'Interaction': 'interaction',
        'Others': 'others',
    }

    class Meta:
        model = BrandingImage
        fields = ['category', 'image', 'retailer_id', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def to_internal_value(self, data):
        """
        Override to map human-readable category names to database keys.
        """
        if 'category' in data:
            human_readable_category = data['category']
            if human_readable_category not in self.CATEGORY_MAP:
                raise serializers.ValidationError({
                    'category': f"'{human_readable_category}' is not a valid category. Allowed values are: {list(self.CATEGORY_MAP.keys())}"
                })
            data['category'] = self.CATEGORY_MAP[human_readable_category]  # Map to database key
        return super().to_internal_value(data)

    def create(self, validated_data):
        # Handle image conversion
        image_data = validated_data.pop('image')

        if ';base64,' not in image_data:
            raise serializers.ValidationError({"image": "Invalid base64 image data. Ensure it includes 'data:image/...;base64,...'."})

        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # Get file extension from MIME type
            file_name = f"{uuid.uuid4()}.{ext}"  # Create unique file name
            image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
        except Exception as e:
            raise serializers.ValidationError({"image": f"Error decoding image: {str(e)}"})

        # Save BrandingImage instance
        branding_image = BrandingImage.objects.create(image=image_file, **validated_data)
        return branding_image



class OrderSerializer(serializers.ModelSerializer):
    retailer_id = serializers.CharField()
    product = serializers.CharField(max_length=255)  # Update to CharField since product is now a string

    class Meta:
        model = Order
        fields = ['retailer_id', 'product', 'quantity', 'delivery', 'interested_in_futur_x', 'timestamp', 'sku']
        read_only_fields = ['timestamp']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    """
    Serializer to handle the validation of the login credentials.
    """
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Ensure that both the username and password are provided.
        """
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")
        
        return data