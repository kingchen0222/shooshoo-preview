import os, json, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI  = 'http://localhost:8080'
SCOPES        = 'https://www.googleapis.com/auth/webmasters https://www.googleapis.com/auth/webmasters.readonly'

auth_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        auth_code = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'<h2>OK! Authorized. You can close this tab.</h2>')
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, *args):
        pass

import urllib.parse
params = {
    'client_id':     CLIENT_ID,
    'redirect_uri':  REDIRECT_URI,
    'response_type': 'code',
    'scope':         SCOPES,
    'access_type':   'offline',
    'prompt':        'consent'
}
auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)

print('Opening browser for Google authorization...')
webbrowser.open(auth_url)

server = HTTPServer(('localhost', 8080), Handler)
server.serve_forever()

if not auth_code:
    print('Authorization failed.')
    exit(1)

# Exchange code for tokens
r = requests.post('https://oauth2.googleapis.com/token', data={
    'code':          auth_code,
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri':  REDIRECT_URI,
    'grant_type':    'authorization_code'
})
tokens = r.json()

if 'refresh_token' not in tokens:
    print('Error:', tokens)
    exit(1)

refresh_token = tokens['refresh_token']
print('Refresh token obtained!')

# Save to .env
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'GOOGLE_REFRESH_TOKEN' in content:
    import re
    content = re.sub(r'GOOGLE_REFRESH_TOKEN=.*', f'GOOGLE_REFRESH_TOKEN={refresh_token}', content)
else:
    content += f'\nGOOGLE_REFRESH_TOKEN={refresh_token}\n'

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Saved to .env!')
print('Token:', refresh_token[:20] + '...')
