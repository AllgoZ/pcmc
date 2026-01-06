from django.shortcuts import render
import feedparser
import requests
from requests.auth import HTTPBasicAuth
import random
import os
from .models import Volunteer
from django.views.decorators.csrf import csrf_exempt
#bannariammanmechanicalworks keys
# api_key = 'key_3cf80f8709ed2c657208ea725c800519'  # Your API key here
# api_secret = 'secret_10e359fe60c0745ec123cb2d84e27b92185ae4a827cd4bc36408ddce6724e5c5'  # Your secret key here


api_key = 'key_9bbea489476d22dbfb8b8596f23b64b5'  # Your API key here
api_secret = 'secret_c9215670809c76e3e1b38fe7d1fc490910d9cd1d62a7f552e7b6bff815c9e5a7'  # Your secret key here


# Base URL of your Tutor LMS API
# base_url = "https://bannariammanmechanicalworks.com/wp-json/tutor/v1"

base_url = "https://globalophthalmicinstitute.com/wp-json/tutor/v1"
endpoint = "/courses"
# Create your views here.
def index(request):
    return render(request,'goi/index.html')



# The course function that retrieves and displays course content
def course(request):
    url = f"{base_url}{endpoint}"

    try:
        # Make the GET request using Basic Authentication
        response = requests.get(url, auth=HTTPBasicAuth(api_key, api_secret))
    
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Parse the response JSON
                data = response.json()
                courses = data.get('data', {}).get('posts', [])

                # If courses are available, list them all
                if isinstance(courses, list) and len(courses) > 0:
                    course_list = []
                    for course in courses:
                        course_list.append({
                            'title': course.get('post_title', 'No Title Found'),
                            'description': course.get('post_content', 'No Description Found'),
                            'course_url': course.get('guid', 'No URL Found')
                        })

                    context = {
                        'courses': course_list
                    }
                    print(context)
                    return render(request, 'goi/Course.html', context)
                else:
                    return render(request, 'goi/Course.html', {'error': "No courses found."})
            except ValueError:
                return render(request, 'goi/Course.html', {'error': "Failed to parse the response as JSON."})
        else:
            return render(request, 'goi/Course.html', {'error': f"Error occurred: {response.status_code} - {response.text}"})
    except Exception as e:
        return render(request, 'goi/Course.html', {'error': f"An error occurred: {e}"})

def lecture(request):
    url = f"{base_url}{endpoint}"  # Replace with your actual API endpoint

    try:
        response = requests.get(url, auth=HTTPBasicAuth(api_key, api_secret))
        # print("Status Code:", response.status_code)
        # print("Response Text:", response.text)
        if response.status_code == 200:
            try:
                data = response.json()
                lectures = data.get('data', {}).get('posts', [])

                # Extract only lectures with "Lecture" in their categories
                lecture_list = []
                for lecture in lectures:
                    # Extract course category
                    categories = lecture.get('course_category', [])
                    category_names = [cat.get('name', 'Unknown') for cat in categories]

                    if 'lecture' in category_names:  # Filter for "Lecture" category
                        # Extract video details
                        video_data = lecture.get('additional_info', {}).get('video', [])
                        video_id = video_data[0].get('source_youtube', '').split('/')[-1] if video_data else None
                        embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None

                        lecture_list.append({
                            'title': lecture.get('post_title', 'No Title Found'),
                            'description': lecture.get('post_content', 'No Description Found'),
                            'lecture_url': embed_url or 'No URL Found',
                            'categories': ', '.join(category_names) if category_names else 'No Category',
                        })

                context = {'lectures': lecture_list}
                return render(request, 'goi/Lecture.html', context)
            except ValueError:
                return render(request, 'goi/Lecture.html', {'error': "Failed to parse the response as JSON."})
        else:
            return render(request, 'goi/Lecture.html', {'error': f"Error: {response.status_code} - {response.text}"})
    except Exception as e:
        return render(request, 'goi/Lecture.html', {'error': f"An error occurred: {e}"})

#def update(request):
#    return render(request,'Update.html')

def updatepage(request):
    return render(request,'goi/UpdatePage.html')

from django.shortcuts import render
from .models import Volunteer

@csrf_exempt
def volunteer(request):
    success_message = None  # To store the success message

    if request.method == 'POST':
        # Retrieve user input directly from POST request
        subject_of_interest = request.POST.get('subject_of_interest')
        topic = request.POST.get('topic')
        sample_work = request.FILES.get('sample_work')  # Handle file upload
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        # Save the data into the database
        Volunteer.objects.using('goi_db').create(
            subject_of_interest=subject_of_interest,
            topic=topic,
            sample_work=sample_work,
            phone_number=phone_number,
            email=email
        )

        # Set the success message
        success_message = "Thank you! Your submission has been received."

    return render(request, 'goi/Volunteer.html', {'success_message': success_message})



def update(request):
    # List of RSS feed URLs
    feed_urls = [
        'https://www.visionmonday.com/rss/eyecare/a-greater-vision/',
        'https://www.visionmonday.com/rss/eyecare/eye-health/'
    ]

    all_news_items = []

    # Assuming your stock images are named "1.jpg", "2.jpg", etc., in the "assets" directory
    stock_images = [f'/static/Assets/thumbnails/{i}.jpg' for i in range(1, 5)]  # Adjust path as needed
    image_count = len(stock_images)  # Define the number of available images
    image_index = 0 
    for feed_url in feed_urls:
        news_feed = feedparser.parse(feed_url)
        items = news_feed.entries

        for entry in items:
            # Randomly assign a stock image from the available images
            thumbnail = stock_images[image_index]

            # Increment the index and reset if it exceeds the available images
            image_index = (image_index + 1) % image_count
            
            all_news_items.append({
                'title': entry.title,
                'link': entry.link,
                'thumbnail': thumbnail,
                'published': entry.published,
            })

    context = {
        'news_items': all_news_items
    }

    return render(request, 'goi/Update.html', context)