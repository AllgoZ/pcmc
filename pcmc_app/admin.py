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
            file_data = csv_file.read()
            
            # Try decoding with different encodings
            try:
                decoded_file = file_data.decode('utf-8-sig') # Handles BOM and strict UTF-8
            except UnicodeDecodeError:
                try:
                    decoded_file = file_data.decode('cp1252') # Common Windows encoding (Excel)
                except UnicodeDecodeError:
                    decoded_file = file_data.decode('latin-1') # Fallback for other single-byte encodings

            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader) # Skip header
            
            # Expected format: TopicName, Standard, Subject, Question, Opt1, Opt2, Opt3, Opt4, Correct, Reason
            success_count = 0
            fail_count = 0
            errors = []

            for i, row in enumerate(reader, start=1):
                try:
                    # Row format: TopicName, Standard, Subject, Question, Opt1, Opt2, Opt3, Opt4, Correct, Reason
                    topic_name = row[0].strip()
                    standard_name = row[1].strip()
                    subject_name = row[2].strip()
                    question_text = row[3].strip()
                    
                    # Handle Options: remove "a) ", "b) " etc if present
                    def clean_option(opt):
                        opt = opt.strip()
                        for prefix in ["a) ", "b) ", "c) ", "d) ", "a)", "b)", "c)", "d)"]:
                            if opt.lower().startswith(prefix):
                                return opt[len(prefix):].strip()
                        return opt

                    opt1 = clean_option(row[4])
                    opt2 = clean_option(row[5])
                    opt3 = clean_option(row[6])
                    opt4 = clean_option(row[7])

                    # Handle Correct Answer: "Answer: b", "b", "2"
                    raw_correct = row[8].lower().replace("answer:", "").strip()
                    map_correct = {'a': 1, 'b': 2, 'c': 3, 'd': 4, '1': 1, '2': 2, '3': 3, '4': 4}
                    correct_option = map_correct.get(raw_correct) # Returns None if not found
                    
                    if not correct_option:
                         # Fallback for direct integer safe-guard
                         try:
                             correct_option = int(raw_correct)
                         except:
                             raise ValueError(f"Invalid correct option: {row[8]}")

                    # Use Standard and Subject to find the specific Topic
                    topic = Topic.objects.filter(
                        name__iexact=topic_name,
                        standard__name__iexact=standard_name,
                        subject__name__iexact=subject_name
                    ).first()
                    
                    if not topic:
                        # Fallback: Try looking up by just topic name if strict match fails (though risky, maybe helpful?)
                        # Or better, just report exact error.
                        raise ValueError(f"Topic '{topic_name}' for Standard '{standard_name}' and Subject '{subject_name}' not found.")

                    Question.objects.create(
                        topic=topic,
                        question_text=question_text,
                        option1=opt1,
                        option2=opt2,
                        option3=opt3,
                        option4=opt4,
                        correct_option=correct_option,
                        reason=row[9] if len(row) > 9 else ""
                    )
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    errors.append(f"Row {i}: {str(e)}")
            
            if success_count > 0:
                self.message_user(request, f"Successfully imported {success_count} questions.")
            if fail_count > 0:
                self.message_user(request, f"Failed to import {fail_count} rows. First few errors: {'; '.join(errors[:3])}", level='error')

            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)
                        
# Customize the admin site headers and titles
admin.site.site_header = "PCMC CONTENT MANAGEMENT"
admin.site.site_title = "PCMC"
admin.site.index_title = "PCMC ADMIN"
