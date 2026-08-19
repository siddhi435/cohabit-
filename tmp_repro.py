import json
import urllib.request
import sys

sys.path.insert(0, '.')
from src.main import load_users
from src.web import build_custom_user
from src.recommender import RecommendationEngine

payload = {
    'name': 'Hiral',
    'profession': 'Student',
    'gender': 'Female',
    'work_shift': 'Morning',
    'personality': 'Introvert',
    'cleanliness': 'Organised',
    'bedtime': '11 PM',
    'wake_time': '7 AM',
    'sleep_type': 'Light Sleeper',
    'noise_preference': 'Quiet',
    'social_energy_rating': 3,
    'room_type_preference': 'Private Room',
    'privacy_importance': 'Medium',
    'pets': 'No Pets',
    'smoking_drinking': 'No Smoking/Drinking',
    'dietary_restrictions': 'No Restrictions',
    'bio': 'I am calm and quiet.'
}

users = load_users()
user = build_custom_user(payload)
engine = RecommendationEngine()
matches = engine.recommend(user, users, limit=5)
print('user', user.name, user.bio)
print('candidates', len(users))
print('matches', len(matches))
for item in matches[:3]:
    print(item['name'], item['score'], item['coach'][:120])
