"""
Scorecard Dashboard - Flask app
Works both locally (python3 app.py) and on Vercel (serverless).

Token is read from:
  - GOOGLE_TOKEN_JSON environment variable  (Vercel / production)
  - ../token.json file                       (local development)
"""
import os
import json

from flask import Flask, jsonify
from flask_cors import CORS
import google.oauth2.credentials
import googleapiclient.discovery
from google.auth.transport.requests import Request

app = Flask(__name__)
CORS(app)

SPREADSHEET_ID = '1LL-uY3lNPCotpTdUcltFBUmfI7nTBH64Cr_eE0uwkC8'
TARGET_SHEET_GID = 1582875063

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INDEX_HTML = os.path.join(_BASE, 'index.html')
_TOKEN_FILE = os.path.join(_BASE, 'token.json')


# ── Credentials ──────────────────────────────────────────────────────────────

def load_credentials():
    """Load OAuth2 credentials from env var (Vercel) or local token.json."""
    token_json = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json:
        data = json.loads(token_json)
    elif os.path.exists(_TOKEN_FILE):
        with open(_TOKEN_FILE) as f:
            data = json.load(f)
    else:
        return None

    creds = google.oauth2.credentials.Credentials(
        token=data.get('token'),
        refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=data.get('client_id'),
        client_secret=data.get('client_secret'),
        scopes=data.get('scopes'),
    )

    # Refresh if expired — access token is not persisted in serverless,
    # but refresh_token is permanent so this always works.
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    with open(_INDEX_HTML) as f:
        return f.read()


@app.route('/api/data')
def get_data():
    creds = load_credentials()
    if not creds:
        return jsonify({
            'error': 'not_authenticated',
            'message': 'Set GOOGLE_TOKEN_JSON environment variable.',
        }), 401

    try:
        service = googleapiclient.discovery.build(
            'sheets', 'v4', credentials=creds, cache_discovery=False)
        api = service.spreadsheets()

        spreadsheet = api.get(spreadsheetId=SPREADSHEET_ID).execute()
        all_sheets = spreadsheet.get('sheets', [])

        target = next(
            (s for s in all_sheets
             if s['properties']['sheetId'] == TARGET_SHEET_GID),
            all_sheets[0] if all_sheets else None,
        )
        if not target:
            return jsonify({'error': 'Sheet not found'}), 404

        sheet_name = target['properties']['title']
        result = api.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_name,
            valueRenderOption='FORMATTED_VALUE',
        ).execute()

        values = result.get('values', [])
        if not values:
            return jsonify({
                'headers': [], 'rows': [], 'sheet_name': sheet_name,
                'all_sheets': [s['properties']['title'] for s in all_sheets],
            })

        headers = values[0]
        rows = [
            (row + [''] * (len(headers) - len(row)))[:len(headers)]
            for row in values[1:]
        ]

        return jsonify({
            'headers': headers,
            'rows': rows,
            'sheet_name': sheet_name,
            'all_sheets': [s['properties']['title'] for s in all_sheets],
            'spreadsheet_title': spreadsheet.get('properties', {}).get('title', ''),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sheet/<sheet_name>')
def get_sheet(sheet_name):
    creds = load_credentials()
    if not creds:
        return jsonify({'error': 'not_authenticated'}), 401

    try:
        service = googleapiclient.discovery.build(
            'sheets', 'v4', credentials=creds, cache_discovery=False)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_name,
            valueRenderOption='FORMATTED_VALUE',
        ).execute()

        values = result.get('values', [])
        if not values:
            return jsonify({'headers': [], 'rows': [], 'sheet_name': sheet_name})

        headers = values[0]
        rows = [
            (row + [''] * (len(headers) - len(row)))[:len(headers)]
            for row in values[1:]
        ]
        return jsonify({'headers': headers, 'rows': rows, 'sheet_name': sheet_name})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
