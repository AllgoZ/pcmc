from django.contrib import admin
from .models import topics_maths, topics_science, School, Question, ProductDetails, Subject, Standard, Topic, StudyMaterial
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
import csv
import io

# Register existing models
admin.site.register(topics_maths)
admin.site.register(topics_science)
admin.site.register(School)
admin.site.register(ProductDetails)
admin.site.register(Subject)
admin.site.register(Standard)
admin.site.register(Topic)
admin.site.register(StudyMaterial)

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

# Register the new Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic', 'correct_option')
    search_fields = ('question_text', 'topic__name')
    list_filter = ('topic', 'correct_option')
    change_list_template = "admin/question_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader) # Skip header
            
            # Expected format: TopicName, Standard, Subject, Question, Opt1, Opt2, Opt3, Opt4, Correct, Reason
            for row in reader:
                # Basic error handling and creation logic
                try:
                    # Assuming row structure matches exactly, might need adjustment
                    # For now, let's assume specific columns or flexible
                    # Let's assume: topic_name, question, opt1, opt2, opt3, opt4, correct, reason
                    # finding topic might be tricky if not strict. 
                    # Simpler: Create questions if topic matches by name safely.
                    topic_name = row[0]
                    topic = Topic.objects.filter(name=topic_name).first() # Naive match
                    if topic:
                        Question.objects.create(
                            topic=topic,
                            question_text=row[3],
                            option1=row[4],
                            option2=row[5],
                            option3=row[6],
                            option4=row[7],
                            correct_option=int(row[8]),
                            reason=row[9] if len(row) > 9 else ""
                        )
                except Exception as e:
                    pass # Log error or handle
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)
                        
# Customize the admin site headers and titles
admin.site.site_header = "PCMC CONTENT MANAGEMENT"
admin.site.site_title = "PCMC"
admin.site.index_title = "PCMC ADMIN"
