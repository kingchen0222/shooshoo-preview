import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

CLIENT_ID     = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
ENV_PATH      = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/adwords"],
)

print("瀏覽器即將開啟，請登入並點「允許」...")
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

refresh_token = creds.refresh_token
print(f"取得 Token：{refresh_token[:12]}...")

with open(ENV_PATH, "r", encoding="utf-8") as f:
    content = f.read()

if "GOOGLE_ADS_REFRESH_TOKEN=" in content:
    lines = [f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}" if l.startswith("GOOGLE_ADS_REFRESH_TOKEN=") else l for l in content.splitlines()]
    content = "\n".join(lines)
else:
    content = content.rstrip() + f"\nGOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n"

with open(ENV_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"已寫入 .env 完成！")
