from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import topics_maths, topics_science, School, Question, Topic, StudyMaterial, Subject, Standard
from .serializers import TopicsMathsSerializer, TopicsScienceSerializer, SchoolSerializer, QuestionSerializer
import random
import feedparser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
# ------------------ Web Views ------------------

def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('subject')
        messages.error(request, 'Invalid username or password.')
        return redirect('home')
    return render(request, 'Home.html')

def subject(request):
    scl = int(request.user.username[0:3])
    content_instances = School.objects.filter(school_id=scl)
    for i, content in enumerate(content_instances, 1):
        content.serial_number = i
    return render(request, 'Subject.html', {'scls': {'content_instances': content_instances}})

def maths(request):
    return render(request, 'Maths.html')

def science(request):
    return render(request, 'Science.html')

def sciencebook(request):
    scl = int(request.user.username[0:3])
    user_section = int(request.user.username[3:5])
    content_instances = School.objects.filter(school_id=scl)
    for i, content in enumerate(content_instances, 1):
        content.serial_number = i
    topics = topics_science.objects.filter(section=user_section).order_by('Topic_order')
    
    # Bridge to new Topic model
    topic_list = list(topics)
    for topic in topic_list:
        # topic.serial_number = topic_list.index(topic) + 1 # safer index
        sub, _ = Subject.objects.get_or_create(name="Science")
        stand, _ = Standard.objects.get_or_create(name=str(user_section))
        
        new_topic, created = Topic.objects.get_or_create(
            name=topic.science_topic,
            subject=sub,
            standard=stand
        )
        topic.new_topic = new_topic
        if new_topic:
             topic.has_questions = Question.objects.filter(topic=new_topic).exists()
             topic.study_material = StudyMaterial.objects.filter(topic=new_topic).first()
        else:
             topic.has_questions = False

    for i, topic in enumerate(topic_list, 1):
        topic.serial_number = i
        
    return render(request, 'Sciencebook.html', {'scis': {'content_instances': topic_list}, 'scls': {'content_instances': content_instances}})

def mathamatics(request):
    scl = int(request.user.username[0:3])
    user_section = int(request.user.username[3:5])
    content_instances = School.objects.filter(school_id=scl)
    for i, content in enumerate(content_instances, 1):
        content.serial_number = i
    topics = topics_maths.objects.filter(section=user_section).order_by('Topic_order')
    
    # Bridge to new Topic model
    topic_list = list(topics)
    for topic in topic_list:
        # Try to find corresponding new Topic or Create it
        # We need the Subject and Standard objects first
        sub, _ = Subject.objects.get_or_create(name="Maths")
        # standard name might vary, but let's try to match user_section
        std_name = f"{user_section}th" # e.g. 8th? or Just 8? Models might need normalization.
        # Check if "8th" exists, else create it. Or just use the number if that's the convention.
        # Let's try to be smart. If user_section is 8, look for "8", "8th", "Standard 8".
        # For simplicity in this bridge: Use "Standard {n}" or just check what exists.
        # Reverting to simple get_or_create with a reasonable default
        
        stand, _ = Standard.objects.get_or_create(name=str(user_section)) # Create "8" if missing
        
        new_topic, created = Topic.objects.get_or_create(
            name=topic.maths_topic,
            subject=sub,
            standard=stand
        )
        
        topic.new_topic = new_topic
        if new_topic:
             topic.has_questions = Question.objects.filter(topic=new_topic).exists()
             topic.study_material = StudyMaterial.objects.filter(topic=new_topic).first()
        else:
             topic.has_questions = False

    for i, topic in enumerate(topic_list, 1):
        topic.serial_number = i
    return render(request, 'Mathamatics.html', {'tops': {'content_instances': topic_list}, 'scls': {'content_instances': content_instances}})

def home_view(request):
    return render(request, 'assessment/index.html')

@xframe_options_exempt
def assessment_view(request, topic_id=None):
    if topic_id:
        request.session['current_topic_id'] = topic_id
    
    is_popup = request.GET.get('popup') == 'true'
    return render(request, 'assessment/assessment.html', {
        'is_popup': is_popup,
        'popup_param': '?popup=true' if is_popup else ''
    })

@xframe_options_exempt
def start_assessment(request, topic_id):
    questions = list(Question.objects.filter(topic_id=topic_id))
    if not questions:
        messages.warning(request, "No questions found for this topic.")
        return redirect('mathamatics') # or generic back
        
    random.shuffle(questions)
    # Store IDs in session
    request.session['questions'] = [q.id for q in questions] # Store all or limit? Limiting to 5 for now
    if len(questions) > 5:
        request.session['questions'] = [q.id for q in questions[:5]]
        
    request.session['answered'] = []
    
    response_url = reverse('question', kwargs={'question_number': 1})
    if request.GET.get('popup') == 'true':
        response_url += '?popup=true'
    return redirect(response_url)


@xframe_options_exempt
def question_view(request, question_number):
    question_ids = request.session.get('questions', [])
    answered = request.session.get('answered', [])
    if not question_ids or question_number > len(question_ids):
        # Result or done
        is_popup = request.GET.get('popup') == 'true'
        return render(request, 'assessment/question.html', {
            'finished': True,
            'is_popup': is_popup,
            'popup_param': '?popup=true' if is_popup else ''
        })
        
    question = Question.objects.get(id=question_ids[question_number - 1])
    feedback = {}
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        if selected_answer:
            selected_option = int(selected_answer)
            is_correct = (selected_option == question.correct_option)
            
            feedback = {
                'show': True,
                'is_correct': is_correct,
                'selected_option': selected_option,
                'correct_option': question.correct_option,
                'correct_text': getattr(question, f'option{question.correct_option}'),
                'correct_image': getattr(question, f'option{question.correct_option}_image'),
                'reason': question.reason
            }
            
            if is_correct and question_number not in answered:
                answered.append(question_number)
                request.session['answered'] = answered
            
    is_popup = request.GET.get('popup') == 'true'

    return render(request, 'assessment/question.html', {
        'question': question,
        'question_number': question_number,
        'total_questions': len(question_ids),
        'finished': len(answered) >= len(question_ids),
        'feedback': feedback,
        'is_popup': is_popup,
        'popup_param': '?popup=true' if is_popup else ''
    })

@xframe_options_exempt
def reload_view(request):
    topic_id = request.session.get('current_topic_id')
    if topic_id:
        questions = list(Question.objects.filter(topic_id=topic_id))
    else:
        questions = list(Question.objects.all())
        
    random.shuffle(questions)
    # Store IDs in session
    request.session['questions'] = [q.id for q in questions] # Store all 
    if len(questions) > 5:
        request.session['questions'] = [q.id for q in questions[:5]] # Limit to 5
        
    request.session['answered'] = []
    # Clear topic_id so standard reload works? Or keep it? keeping it is fine.
    
    response_url = reverse('question', kwargs={'question_number': 1})
    if request.GET.get('popup') == 'true':
        response_url += '?popup=true'
    return redirect(response_url)

def rss_news_view(request):
    feed_urls = [
        'https://ww2.kqed.org/mindshift/feed/',
        'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'https://feeds.bbci.co.uk/news/rss.xml'
    ]
    news_items = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            thumb = entry.media_thumbnail[0]['url'] if 'media_thumbnail' in entry else (
                entry.media_content[0]['url'] if 'media_content' in entry else None)
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'thumbnail': thumb,
                'published': entry.published,
            })
    return render(request, 'assessment/news_template.html', {'news_items': news_items})

# ------------------ API Views ------------------


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "standard": f"Standard {int(username[3:5])}",
                "school_id": username[:3]
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class MathsTopicsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        standard = int(username[3:5])
        topics = topics_maths.objects.filter(section=standard).order_by('Topic_order')
        serializer = TopicsMathsSerializer(topics, many=True, context={'request': request})  # <- add context
        return Response(serializer.data)

class ScienceTopicsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        standard = int(username[3:5])
        topics = topics_science.objects.filter(section=standard).order_by('Topic_order')
        serializer = TopicsScienceSerializer(topics, many=True, context={'request': request})  # ✅ context passed
        return Response(serializer.data)


class SchoolInfoAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        school_id = int(request.user.username[:3])
        schools = School.objects.filter(school_id=school_id)
        return Response(SchoolSerializer(schools, many=True).data)


class AssessmentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = list(Question.objects.all())
        random.shuffle(questions)
        return Response(QuestionSerializer(questions[:3], many=True).data)