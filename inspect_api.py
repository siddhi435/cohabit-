import json
import urllib.request

payload = {
    'name':'Hiral','profession':'Student','gender':'Female','work_shift':'Morning',
    'personality':'Introvert','cleanliness':'Organised','bedtime':'11 PM','wake_time':'7 AM',
    'sleep_type':'Light Sleeper','noise_preference':'Quiet','social_energy_rating':3,
    'room_type_preference':'Private Room','privacy_importance':'Medium','pets':'No Pets',
    'smoking_drinking':'No Smoking/Drinking','dietary_restrictions':'No Restrictions',
    'bio':'I am calm and quiet.'
}
req = urllib.request.Request('http://127.0.0.1:8000/api/custom-matches', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req) as response:
    data = json.load(response)
    print('matches:', len(data.get('matches', [])))
    print('first match keys:', list(data['matches'][0].keys()))
    print('first match:', data['matches'][0])
