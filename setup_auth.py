"""
Run this ONCE to authorize the app with your Google account.

Usage:
    python3 setup_auth.py

It will print a URL — open it in your Windows browser.
After you authorize, the token is saved automatically.
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

PORT = 8080


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)

    print()
    print("=" * 65)
    print("  Starting local auth server on port", PORT)
    print()
    print("  STEP 1 — Open this URL in your Windows browser:")
    print()

    # run_local_server starts an HTTP server on localhost:PORT waiting for
    # the OAuth redirect. WSL2 shares localhost with Windows so this works.
    # open_browser=False lets us print the URL ourselves.
    creds = flow.run_local_server(
        port=PORT,
        open_browser=False,
        success_message="Authorization complete! You can close this tab and return to the terminal.",
    )

    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else [],
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print()
    print("  Authorization successful! Token saved.")
    print("  Start the dashboard with:  python3 app.py")
    print()


if __name__ == '__main__':
    main()
