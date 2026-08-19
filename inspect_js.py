import urllib.request

req = urllib.request.Request('http://127.0.0.1:8000/app.js')
with urllib.request.urlopen(req) as response:
    text = response.read().decode()
    print(text[:600])
