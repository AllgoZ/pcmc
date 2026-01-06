from rest_framework import serializers
from .models import topics_maths, topics_science, School, Question


class TopicsMathsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    title = serializers.CharField(source='maths_topic')
    video_url = serializers.SerializerMethodField()
    description = serializers.CharField(source='text_content')

    class Meta:
        model = topics_maths
        fields = ['Topic_order', 'title', 'image', 'video_url', 'description']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            return request.build_absolute_uri(obj.img.url)
        return None

    def get_video_url(self, obj):
        # Assuming `maths_link` holds the YouTube ID or full URL
        if "http" in obj.maths_link:
            return obj.maths_link
        return f"https://www.youtube.com/watch?v={obj.maths_link}"

class TopicsScienceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    title = serializers.CharField(source='science_topic')
    video_url = serializers.SerializerMethodField()
    description = serializers.CharField(source='text_content')

    class Meta:
        model = topics_science
        fields = ['Topic_order', 'title', 'image', 'video_url', 'description']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            return request.build_absolute_uri(obj.img.url)
        return None

    def get_video_url(self, obj):
        # Assuming `science_link` holds the YouTube ID or full URL
        if "http" in obj.science_link:
            return obj.science_link
        return f"https://www.youtube.com/watch?v={obj.science_link}"

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
