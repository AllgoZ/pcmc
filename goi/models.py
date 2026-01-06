from django.db import models

class Volunteer(models.Model):
    subject_of_interest = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    sample_work = models.FileField(upload_to='uploads/', null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    class Meta:
        app_label = 'goi'
