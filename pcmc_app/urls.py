from django.urls import path
from . import views
from .views import assessment_view, question_view, reload_view, home_view, rss_news_view
from .views import (
    LoginAPIView, MathsTopicsAPIView, ScienceTopicsAPIView,
    SchoolInfoAPIView, AssessmentAPIView
)
urlpatterns =[
    path('', views.home, name ='home'),
    path('subject/',views.subject,name='subject'),
    path('maths/',views.maths,name='maths'),
    path('science/',views.science,name='science'),
    path('sciencebook/',views.sciencebook,name='sciencebook'),
    path('mathamatics/',views.mathamatics,name='mathamatics'),
    path('', home_view, name='index'),  # Home page
    path('assessment/', assessment_view, name='assessment'),  # Assessment landing page
    path('assessment/<int:topic_id>/', assessment_view, name='assessment_topic'),
    path('start-assessment/<int:topic_id>/', views.start_assessment, name='take_assessment'), # Direct start if needed
    path('question/<int:question_number>/', question_view, name='question'),  # Question pages
    path('reload/', reload_view, name='reload'),
    path('news/', rss_news_view, name='rss_news'),
    
    path('api/login/', LoginAPIView.as_view()),
    path('api/topics/maths/', MathsTopicsAPIView.as_view()),
    path('api/topics/science/', ScienceTopicsAPIView.as_view()),
    path('api/school/', SchoolInfoAPIView.as_view()),
    path('api/assessment/', AssessmentAPIView.as_view()),
]