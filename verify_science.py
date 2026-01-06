import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcmc.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from pcmc_app.models import Subject, Standard, Topic, StudyMaterial, topics_science
from django.core.files.base import ContentFile

def verify():
    # Setup Data
    username = "10008001"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password")
        user.save()

    # Create dummy science legacy topic if needed
    t_sci, _ = topics_science.objects.get_or_create(
        section=8, 
        Topic_order=1, 
        science_topic="Force",
        defaults={'science_link': 'video_id_sci', 'text_content': 'Force content'}
    )
    
    # Bridge objects
    sub, _ = Subject.objects.get_or_create(name="Science")
    std, _ = Standard.objects.get_or_create(name="8")
    topic, _ = Topic.objects.get_or_create(name="Force", subject=sub, standard=std)
    
    if not StudyMaterial.objects.filter(topic=topic).exists():
        StudyMaterial.objects.create(topic=topic, title="Sci PDF", pdf_file=ContentFile(b"dummy link", name="scitest.pdf"))

    c = Client()
    c.force_login(user)
    
    print("Checking Sciencebook...")
    try:
        resp = c.get('/sciencebook/')
        if resp.status_code == 200:
            content = resp.content.decode()
            
            # Check for Video ID
            if "video_id_sci" in content or "youtube-nocookie.com/embed/" in content:
                print("SUCCESS: Video link found.")
            else:
                print("FAILURE: Video link MISSING.")

            if "Q/A" in content:
                print("SUCCESS: Q/A text found.")
            else:
                 print("FAILURE: Q/A text MISSING.")
                 
            if "Take Assessment" in content:
                print("SUCCESS: Take Assessment text found.")
            else:
                 print("FAILURE: Take Assessment text MISSING.")

        else:
            print(f"FAILURE: Status code {resp.status_code}")
    except Exception as e:
        print(f"FAILURE: Exception {e}")

if __name__ == "__main__":
    verify()
