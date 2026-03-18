"""Local development server — run with: python3 app.py"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from api.index import app

if __name__ == '__main__':
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'token.json')):
        print("No token.json found. Run: python3 setup_auth.py")
    else:
        print("Dashboard starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
