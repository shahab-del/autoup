"""One-time OAuth bootstrap on your own computer; never commit credentials."""
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    print("Save securely as YOUTUBE_TOKEN_JSON; do not commit:")
    print(credentials.to_json())

if __name__ == "__main__":
    main()
