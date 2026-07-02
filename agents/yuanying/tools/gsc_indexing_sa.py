"""
Google Indexing API via Service Account
"""
import json, time, requests
from pathlib import Path

KEY_FILE = Path('D:/咻咻打包CLAUDE/gen-lang-client-0901966054-8a6f63d2e942.json')
URLS = [
    'https://www.shooshoo.com.tw/tainan-convenience-store-shipping/',
    'https://www.shooshoo.com.tw/convenience-store-pickup-guide/',
]

# 用 google-auth 換 token
try:
    from google.oauth2 import service_account
    import google.auth.transport.requests as ga_requests
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_FILE),
        scopes=['https://www.googleapis.com/auth/indexing']
    )
    creds.refresh(ga_requests.Request())
    token = creds.token
    print(f'SA token OK')
except ImportError:
    # fallback: 手動 JWT
    import base64, hashlib, time as t
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import json as j

    key_data = j.loads(KEY_FILE.read_text())
    private_key_pem = key_data['private_key']
    client_email    = key_data['client_email']

    now = int(t.time())
    header  = base64.urlsafe_b64encode(j.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b'=')
    payload = base64.urlsafe_b64encode(j.dumps({
        "iss": client_email,
        "scope": "https://www.googleapis.com/auth/indexing",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now
    }).encode()).rstrip(b'=')

    from cryptography.hazmat.backends import default_backend
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None, backend=default_backend()
    )
    sig_input = header + b'.' + payload
    sig = base64.urlsafe_b64encode(
        private_key.sign(sig_input, padding.PKCS1v15(), hashes.SHA256())
    ).rstrip(b'=')
    jwt = (sig_input + b'.' + sig).decode()

    r = requests.post('https://oauth2.googleapis.com/token', data={
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': jwt
    })
    token = r.json().get('access_token')
    print(f'JWT token: {"OK" if token else r.json()}')

H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

for url in URLS:
    r = requests.post(
        'https://indexing.googleapis.com/v3/urlNotifications:publish',
        headers=H,
        json={'url': url, 'type': 'URL_UPDATED'}
    )
    print(f'{r.status_code} | {url}')
    if r.status_code != 200:
        print(f'  {r.text[:200]}')
    time.sleep(1)
