import json
import urllib.request
from urllib.error import HTTPError, URLError

# Crucial: Ensure this is spelled perfectly with NO typos or trailing characters
url = "http://127.0.0.1:8000/api/custom-matches"
payload = {
    'name': 'Test Student',
    'profession': 'Student',
    'gender': 'Female',
    'preferred_gender': 'Any',
    'work_shift': 'Morning',
    'personality': 'Introvert',
    'cleanliness': 'Organised',
    'bedtime': '11 PM',
    'wake_time': '7 AM',
    'sleep_type': 'Light Sleeper',
    'noise_preference': 'Quiet',
    'social_energy_rating': '3',
    'room_type_preference': 'Private Room',
    'privacy_importance': 'Medium',
    'pets': 'No Pets',
    'smoking_drinking': "Okay with Roommate's Habits",
    'dietary_restrictions': 'No Restrictions',
    'bio': 'I am calm person'
}

# Convert payload data safely to bytes
data_bytes = json.dumps(payload).encode('utf-8')

# Setup request configuration
req = urllib.request.Request(
    url, 
    data=data_bytes, 
    headers={'Content-Type': 'application/json'}
)

print("Sending profile data payload to server at: {}".format(url))

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('Success. Server responded with status:', resp.status)
        body = resp.read().decode()
        print('Response body:', body)
except HTTPError as e:
    print('HTTP Error Code:', e.code)
    print(e.read().decode())
except URLError as e:
    print('URL Error:', e)
except Exception as e:
    print('Unexpected error occurred:', e)
