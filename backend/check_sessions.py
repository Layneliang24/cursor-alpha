import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import TypingPracticeSession
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='testuser')
sessions = TypingPracticeSession.objects.filter(user=user)

print(f'Total sessions: {sessions.count()}')
if sessions.exists():
    print(f'Date range: {sessions.earliest("session_date").session_date} to {sessions.latest("session_date").session_date}')
    print('Sample sessions:')
    for s in sessions[:10]:
        print(f'  {s.session_date} - Words: {s.total_words}, Completed: {s.is_completed}')
else:
    print('No sessions found')