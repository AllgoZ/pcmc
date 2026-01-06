import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcmc.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
# Ensure we have the user
username = "10008001"
user, created = User.objects.get_or_create(username=username)
if created:
    user.set_password("password")
    user.save()

c = Client()
c.force_login(user)

print("Fetching Sciencebook...")
resp = c.get('/sciencebook/')
content = resp.content.decode()

# Find all occurrences of openVideoModal
import re
matches = re.findall(r"openVideoModal\('([^']*)', '([^']*)'\)", content)

print(f"Found {len(matches)} video links:")
for i, (link, topic) in enumerate(matches):
    print(f"{i+1}. Topic: {topic}, Link: {link}")
