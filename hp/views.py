from django.shortcuts import render, redirect
from .models import HpPersonaldetails,Location,ProductDetails,BrandingImage,Item,Order
from django.contrib.auth import authenticate, login
from django.contrib import messages
#from pcmc_app.models import ProductDetails # Import ProductDetails model from the pcmc app
from django.http import JsonResponse
from .serializers import ItemSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import HpPersonaldetailsSerializer, BrandingImageSerializer, OrderSerializer, LoginSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
# The index view to handle the login form
LOCATION_CODES = [
    "Ahe","Ahm", "Ban", "Bho", "Bhu", "Cha", "Che", "Coc", "Del",
    "Jai", "Kol", "Luc", "Mum", "Nag", "Pat", "Pun", "Rai", "Ran", "Sec", "Vis"
]
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()  # Get all items
    serializer_class = ItemSerializer  # Use the ItemSerializer


class LoginApiView(APIView):
    """
    Handles login and token generation for the mobile app.
    The mobile app will send a POST request with 'username' and 'password'.
    """
    
    def post(self, request, *args, **kwargs):
        # Validate incoming data using the LoginSerializer
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            # Extract username and password from validated data
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            # Authenticate user
            user = authenticate(username=username, password=password)

            if user is not None:
                # Authentication successful, generate token
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "message": "Login successful", 
                        "token": token.key  # Send the token back to the mobile app
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                # Authentication failed
                return Response(
                    {"message": "Invalid credentials"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            # If serializer is invalid, return the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def index(request):
    if request.method == 'POST':
        # Get form data
        user_id = request.POST.get('user-id')
        password = request.POST.get('password')
        ro_selection = request.POST.get('ro')
        
        # Attempt to authenticate the user
        user = authenticate(request, username=user_id, password=password)
        #print(user)
        #print(ro_selection)
        if user is not None:
            # Check if the first three characters of user_id match the selected Ro option
            if user_id[:3] == ro_selection and ro_selection in LOCATION_CODES:
                # Successfully authenticated and location check passed
                
                login(request, user)
                messages.success(request, "Login Successful")
                return redirect('selection')  # Redirect to dashboard or selection page
            else:
                # Location check failed
                messages.error(request, "User ID does not match selected Ro option.")
        else:
            # Invalid login details
            messages.error(request, 'Invalid credentials. Please check your user ID and password.')

        return redirect('index')  # Redirect back to login page
    
    # Render login page for GET request
    return render(request, 'index.html')


def catalog(request):
    # Fetch all products from the ProductDetails model
    products = ProductDetails.objects.all()

    # Filter products by category
    mco_products = products.filter(category='mco')  # Motorcycle Oil
    deo_products = products.filter(category='deo')  # Diesel Engine Oil
    pco_products = products.filter(category='pco')  # Passenger Car Oil

    context = {
        'mco_products': mco_products,
        'deo_products': deo_products,
        'pco_products': pco_products,
    }

    return render(request, 'catalog.html', context)



def dashboard(request):
    return render(request, 'dashboard.html')

def personaldetails(request):
    if request.method == 'POST':
        # Collect form data from POST request
        district_name = request.POST.get('district')
        other_district = request.POST.get('otherDistrict')
        town_name = request.POST.get('town')
        other_town = request.POST.get('otherTown')
        outlet_name = request.POST.get('outletName')
        owner_name = request.POST.get('ownerName')
        contact_number = request.POST.get('contactNumber')
        address = request.POST.get('Address')
        pragati_app_enrolled = request.POST.get('hungamaApp')  # Can be "Yes", "No", or other
        existing_hpcl_customer = request.POST.get('hpclCustomer')
        #interested_in_futur_x = request.POST.get('futurX')
        branding_flanges = request.POST.get('flanges')
        branding_danglers = request.POST.get('danglers')
        most_sold_lube = request.POST.get('mostSoldLube')
        application_of_lube = request.POST.get('applicationLube')

        # Check if the form has the essential fields filled
        if not pragati_app_enrolled or not district_name or not town_name or not outlet_name:
            # If required fields are missing, show a message but do not save data
            messages.warning(request, "Please fill all the required fields or skip to proceed.")
            return redirect('catalog')  # Redirect to the catalog page without saving data

        # If all required fields are filled, proceed to save the data
        personal_detail = HpPersonaldetails(
            district=district_name,
            other_district=other_district,
            town=town_name,
            other_town=other_town,
            outlet_name=outlet_name,
            owner_name=owner_name,
            contact_number=contact_number,
            address=address,
            pragati_app_enrolled=pragati_app_enrolled,
            existing_hpcl_customer=existing_hpcl_customer,
            #interested_in_futur_x=interested_in_futur_x,
            branding_flanges=branding_flanges,
            branding_danglers=branding_danglers,
            most_sold_lube=most_sold_lube,
            application_of_lube=application_of_lube
        )
        personal_detail.save()

        # Success message if the form is successfully saved
        messages.success(request, "Personal details submitted successfully.")
        return redirect('catalog')

    else:
        # Get user_id and extract the first 3 characters to determine the region
        user_id = request.user.username  # Assuming the logged-in user's username is the user_id
        region_code = user_id[:3]  # Get the first 3 letters from user_id

        # Filter locations based on the region code (region)
        locations = Location.objects.filter(region__istartswith=region_code)

        # Initialize empty lists for districts and towns
        districts = []
        towns = []

        # Get the distinct districts for the selected region
        districts = Location.objects.filter(region__istartswith=region_code).values('district').distinct()

        # Get the distinct towns for the selected region's districts
        towns = Location.objects.filter(district__in=[district['district'] for district in districts]).values('town').distinct()

        context = {
            'districts': districts,
            'towns': towns,
        }

        return render(request, 'personaldetails.html', context)

def selection(request):
    return render(request, 'selection.html')

def thankyou(request):
    return render(request, 'thankyou.html')

def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Get the image and category from the POST data
        image = request.FILES['image']
        category = request.POST.get('category')

        if category and image:
            # Create a new BrandingImage object and save it
            branding_image = BrandingImage(category=category, image=image)
            branding_image.save()

            # Add a success message
            messages.success(request, f"Image uploaded successfully for category: {category}!")
            return redirect('selection')  # Redirect to branding page or another page after successful upload
        else:
            # If no category or image is provided, show an error message
            messages.error(request, "Please select an image and a category.")
            return redirect('upload')  # Redirect back to the upload page in case of an error
    else:
        return render(request, 'upload.html')  # Render the upload page if it's a GET request


def quiz(request):
    return render(request, 'quiz.html')


class HpPersonaldetailsUpdateView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permission checks

    def post(self, request, *args, **kwargs):
        serializer = HpPersonaldetailsSerializer(data=request.data)
        if serializer.is_valid():
            # Save or update the record
            personal_detail, created = HpPersonaldetails.objects.update_or_create(
                contact_number=serializer.validated_data['contact_number'],  # Assuming this is unique
                defaults=serializer.validated_data
            )
            message = "Created" if created else "Updated"
            return Response(
                {
                    "message": f"Personal details {message} successfully!",
                    "data": HpPersonaldetailsSerializer(personal_detail).data,
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# API for BrandingImage
class BrandingImageUpdateView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permission checks

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of branding images in the request data."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        responses = []  # To collect responses for each branding image
        errors = []  # To collect errors for invalid branding images

        for image_data in request.data:
            serializer = BrandingImageSerializer(data=image_data)
            if serializer.is_valid():
                # Save the branding image
                branding_image = serializer.save()
                responses.append({
                    "message": "Branding image created successfully!",
                    "data": BrandingImageSerializer(branding_image).data,
                })
            else:
                errors.append({"error": serializer.errors, "image_data": image_data})

        status_code = status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS
        return Response({"responses": responses, "errors": errors}, status=status_code)


    
# API for Order
class OrderUpdateView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permission checks

    def post(self, request, *args, **kwargs):
        orders_data = request.data.get('order')  # Extract the 'order' key
        if not orders_data or not isinstance(orders_data, list):
            return Response(
                {"error": "Expected 'order' field with a list of orders."},
                status=status.HTTP_400_BAD_REQUEST
            )

        responses = []  # To store successful order creation/update messages
        errors = []  # To store errors for invalid orders

        for order_data in orders_data:
            # Validate each order
            serializer = OrderSerializer(data=order_data)
            if serializer.is_valid():
                # Update or create the order
                order, created = Order.objects.update_or_create(
                    retailer_id=serializer.validated_data['retailer_id'],
                    product=serializer.validated_data['product'],
                    defaults=serializer.validated_data,
                )
                message = "Created" if created else "Updated"
                responses.append({
                    "message": f"Order {message} successfully!",
                    "data": OrderSerializer(order).data,
                })
            else:
                # Capture errors for this order
                errors.append({
                    "error": serializer.errors,
                    "order_data": order_data
                })

        status_code = status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS
        return Response(
            {
                "responses": responses,
                "errors": errors,
            },
            status=status_code
        )




    
# API for Login
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate or retrieve token for the authenticated user
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)