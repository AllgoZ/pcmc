from django.db import models

# Create your models here.
    
class topics_maths(models.Model):
    Topic_order = models.IntegerField()
    section = models.IntegerField()
    maths_topic= models.CharField(max_length=100)
    #maths_link = models.URLField(max_length=500)
    maths_link = models.CharField(max_length=500)
    subject=models.CharField(max_length=200)
    text_content=models.TextField()
    img= models.ImageField(upload_to='pics', default='default_media\Motion.png')
    Topic_enable = models.BooleanField(default=True)
    def __str__(self):
        return f"Section : {self.section} - {self.maths_topic} - {self.Topic_order}"    
    
class topics_science(models.Model):
    Topic_order = models.IntegerField()
    section = models.IntegerField()
    science_topic= models.CharField(max_length=100)
    #science_link = models.URLField(max_length=500)
    science_link = models.CharField(max_length=500)
    subject=models.CharField(max_length=200)
    text_content=models.TextField()
    img= models.ImageField(upload_to='pics', default='default_media\Motion.png')
    Topic_enable = models.BooleanField(default=True)
    def __str__(self):
        #return f"{self.section} - {self.science_topic}"
        return f"Section : {self.section} - {self.science_topic} - {self.Topic_order}"
    
class School(models.Model):
    school_name = models.CharField(max_length=100)
    school_id = models.IntegerField(unique=True)
    school_logo = models.ImageField(upload_to='school_logos/')
    def __str__(self):
        return self.school_name

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Standard(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.subject} - {self.standard} - {self.name}"

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField()  # Store the correct option number (1-4)
    reason = models.TextField(blank=True, null=True)
    
    # Image fields for question and options
    question_image = models.ImageField(upload_to='assessment_images/', null=True, blank=True)
    option1_image = models.ImageField(upload_to='assessment_images/', null=True, blank=True)
    option2_image = models.ImageField(upload_to='assessment_images/', null=True, blank=True)
    option3_image = models.ImageField(upload_to='assessment_images/', null=True, blank=True)
    option4_image = models.ImageField(upload_to='assessment_images/', null=True, blank=True)

    def __str__(self):
        return self.question_text

class StudyMaterial(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='study_materials/')
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Material for {self.topic}"

class ProductDetails(models.Model):
    CATEGORY_CHOICES = [
        ('two_wheeler', 'Two Wheeler'),
        ('four_wheeler', 'Four Wheeler'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/')
    quantity_1l = models.IntegerField(default=0)
    quantity_2l = models.IntegerField(default=0)
    quantity_5l = models.IntegerField(default=0)
    applications = models.TextField()
    features = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.category}"