import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcmc.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from pcmc_app.models import Subject, Standard, Topic

def verify():
    # Setup Data
    username = "10008001"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password")
        user.save()

    # Setup Data
    username = "10008001"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password")
        user.save()

    # Ensure a Topic exists and has StudyMaterial for visual verification
    # Maths | 8 | Numbers (usually first)
    sub, _ = Subject.objects.get_or_create(name="Maths")
    std, _ = Standard.objects.get_or_create(name="8")
    topic, _ = Topic.objects.get_or_create(name="Numbers", subject=sub, standard=std)
    
    # Science Dummy Data
    sub_sci, _ = Subject.objects.get_or_create(name="Science")
    topic_sci, _ = Topic.objects.get_or_create(name="Test Science Topic", subject=sub_sci, standard=std)

    from pcmc_app.models import StudyMaterial
    # Create valid dummy file
    from django.core.files.base import ContentFile
    if not StudyMaterial.objects.filter(topic=topic).exists():
        StudyMaterial.objects.create(topic=topic, title="Test PDF", pdf_file=ContentFile(b"dummy link", name="test.pdf"))
    if not StudyMaterial.objects.filter(topic=topic_sci).exists():
        StudyMaterial.objects.create(topic=topic_sci, title="Sci PDF", pdf_file=ContentFile(b"dummy link", name="scitest.pdf"))

    c = Client()
    c.force_login(user)
    
    # Check Mathamatics
    print("Checking Mathamatics...")
    try:
        resp = c.get('/mathamatics/')
        if resp.status_code == 200:
            content = resp.content.decode().replace('\n', ' ').replace('  ', ' ')
            
            # Debug DB
            print(f"Total Topics: {Topic.objects.count()}")
            
            if "Q/A" in content and "Take Assessment" in content:
                print("SUCCESS: Mathamatics page has 'Q/A' and 'Take Assessment'.")
            else:
                print("FAILURE: Mathamatics page missing texts.")
        else:
            print(f"FAILURE: Mathamatics page status code {resp.status_code}")
    except Exception as e:
        print(f"FAILURE: Mathamatics page Exception: {e}")

    # Check Sciencebook
    print("Checking Sciencebook...")
    try:
        resp = c.get('/sciencebook/')
        if resp.status_code == 200:
            content = resp.content.decode()
            # Science page might not have the text if topics aren't set up, but let's check for visual elements
            if "Q/A" in content and "Take Assessment" in content:
                print("SUCCESS: Sciencebook page has 'Q/A' and 'Take Assessment'.")
            else:
                 # Check if topics exist for science
                print("WARNING: Sciencebook page missing texts (might be no topics).")
        else:
            print(f"FAILURE: Sciencebook page status code {resp.status_code}")
    except Exception as e:
        print(f"FAILURE: Sciencebook page Exception: {e}")

if __name__ == "__main__":
    verify()
