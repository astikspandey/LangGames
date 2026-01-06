#!/usr/bin/env python3
"""
Production server for LangGames - optimized for Render deployment
This script skips venv setup and runs directly with system Python
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import time
import threading
import json
import logging
from datetime import datetime

# Import dependencies (should already be installed in Render environment)
try:
    from walkerauth_client import WalkerAuthClient
    from pastebin_client import create_pastebin_client
    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Make sure all dependencies from requirements.txt are installed")
    DEPENDENCIES_OK = False
    sys.exit(1)

# Check for 'net' parameter to enable network hosting
if 'net' in sys.argv:
    HOST = '0.0.0.0'  # Bind to all network interfaces
    print("Network mode enabled - accessible from other devices")
else:
    HOST = '0.0.0.0'  # Always use 0.0.0.0 on Render
    print("Running in server mode")

PORT = int(os.getenv('PORT', '2937'))

# WalkerAuth Configuration
WALKERAUTH_SECRET_KEY = "langgames_secret_key_12345"
walkerauth_client = WalkerAuthClient(WALKERAUTH_SECRET_KEY)

# Initialize Pastebin client
supabase_client = None

def load_supabase_credentials():
    """Load Pastebin credentials from environment variables or .env file"""
    # First, try environment variables (for Render/production)
    pastebin_url = os.getenv('PASTEBIN_URL')
    site_id = os.getenv('SITE_ID')
    secret_key = os.getenv('SECRET_KEY')

    # If not found, try reading from .env file (for local development)
    if not pastebin_url or not site_id or not secret_key:
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('PASTEBIN_URL=') and not pastebin_url:
                        pastebin_url = line.split('=', 1)[1]
                    elif line.startswith('SITE_ID=') and not site_id:
                        site_id = line.split('=', 1)[1]
                    elif line.startswith('SECRET_KEY=') and not secret_key:
                        secret_key = line.split('=', 1)[1]

    return pastebin_url, site_id, secret_key

def init_supabase():
    """Initialize Pastebin client"""
    global supabase_client

    pastebin_url, site_id, secret_key = load_supabase_credentials()

    if pastebin_url and site_id and secret_key:
        try:
            supabase_client = create_pastebin_client(pastebin_url, site_id, secret_key)
            print(f"✓ Pastebin connected: {pastebin_url}")
            return supabase_client
        except Exception as e:
            print(f"✗ Pastebin connection failed: {e}")
            return None
    else:
        print("ℹ Pastebin credentials not configured")
        print("  Required: PASTEBIN_URL, SITE_ID, SECRET_KEY")
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize Supabase on startup
logger.info("🚀 Starting LangGames server...")
init_supabase()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="src", **kwargs)

    def log_message(self, format, *args):
        # Suppress default logging
        pass

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Serve landing page at root
        if self.path == '/':
            self.path = '/landing.html'
        # Serve game at /game
        elif self.path == '/game':
            self.path = '/index.html'

        # Handle API endpoints
        if self.path.startswith('/api/data/load'):
            # Load data from Supabase only
            try:
                logger.info(f"📥 Load request: {self.path}")

                if not supabase_client:
                    logger.error("❌ Database not configured")
                    self.send_response(503)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Database not configured"}).encode())
                    return

                # Parse user_id from query params if available
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(self.path)
                params = parse_qs(parsed_url.query)
                user_id = params.get('user_id', ['default_user'])[0]

                logger.info(f"🔍 Querying pastebin for user: {user_id}")

                # Query Supabase
                result = supabase_client.table('GIDbasedlv').select('*').eq('user_id', user_id).order('updated_at', desc=True).limit(1).execute()

                if result.data and len(result.data) > 0:
                    # Use the most recent save
                    data = result.data[0]
                    logger.info(f"✅ Loaded data for user {user_id}: level={data.get('level', 0)}, score={data.get('score', 0)}")
                else:
                    logger.info(f"ℹ️  No data found for user: {user_id}")
                    data = {}

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                logger.error(f"❌ Load error: {type(e).__name__}: {str(e)}", exc_info=True)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif self.path.startswith('/auth/success'):
            # Handle WalkerAuth success redirect
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            token = params.get('token', [None])[0]

            if not token:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No token provided</h1></body></html>')
                return

            # Verify token and get user data
            user_data = walkerauth_client.verify_session(token)

            if not user_data:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: Invalid or expired token</h1></body></html>')
                return

            # Send success page with user data
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Successful - LangGames</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
            text-align: center;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        .success-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        .user-info {{
            background: #f7f7f7;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .redirect-message {{
            color: #666;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Authentication Successful!</h1>
        <div class="user-info">
            <p><strong>{user_data.get('username', 'User')}</strong></p>
            <p>{user_data.get('email', '')}</p>
        </div>
        <p class="redirect-message">Redirecting to LangGames...</p>
    </div>
    <script>
        localStorage.setItem('walkerauth_token', '{token}');
        localStorage.setItem('user_email', '{user_data.get('email', '')}');
        localStorage.setItem('user_name', '{user_data.get('username', '')}');
        localStorage.setItem('user_avatar', '{user_data.get('profilePictureUrl', '')}');
        setTimeout(() => {{
            window.location.href = '/game';
        }}, 2000);
    </script>
</body>
</html>
            '''
            self.wfile.write(html.encode())
            return

        # Default file serving
        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'

        # Handle WalkerAuth OAuth callback
        if self.path == '/oauth/callback':
            try:
                data = json.loads(post_data.decode())
                encrypted = data.get('encrypted')
                iv = data.get('iv')
                site_id = data.get('siteId')

                logger.info(f"📝 Received OAuth callback from {site_id}")

                # Decrypt user data
                user_data = walkerauth_client.decrypt_user_data(encrypted, iv)

                if not user_data:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Failed to decrypt user data"}).encode())
                    return

                logger.info(f"✓ Authenticated user: {user_data.get('username')} ({user_data.get('email')})")

                # Generate session token
                token = walkerauth_client.generate_session_token(user_data)

                # Return success with token
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "token": token}).encode())

            except Exception as e:
                logger.error(f"✗ Error in OAuth callback: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        # Handle save data request
        if self.path.startswith('/api/data/save'):
            try:
                data = json.loads(post_data.decode())
                logger.info(f"💾 Save request for user: {data.get('user_id', 'default_user')}")

                # Save to database (encrypted pastebin)
                if not supabase_client:
                    logger.error("❌ Database not configured")
                    self.send_response(503)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Database not configured"}).encode())
                    return

                # Get user_id from data or use default
                user_id = data.get('user_id', 'default_user')

                # Prepare data for Supabase
                supabase_data = {
                    'user_id': user_id,
                    'level': data.get('level', 0),
                    'score': data.get('score', 0),
                    'highScore': data.get('highScore', 0),
                    'gamesPlayed': data.get('gamesPlayed', 0),
                    'stats': data.get('stats', {}),
                    'lastPlayed': data.get('lastPlayed', ''),
                    'updated_at': 'now()'
                }

                logger.info(f"📊 Saving: level={supabase_data['level']}, score={supabase_data['score']}, highScore={supabase_data['highScore']}")

                # Check if record exists
                existing = supabase_client.table('GIDbasedlv').select('id').eq('user_id', user_id).execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing record
                    logger.info(f"🔄 Updating existing record for user: {user_id}")
                    result = supabase_client.table('GIDbasedlv').update(supabase_data).eq('user_id', user_id).execute()
                    logger.info(f"✅ Updated pastebin data for user: {user_id}")
                else:
                    # Insert new record
                    logger.info(f"➕ Creating new record for user: {user_id}")
                    result = supabase_client.table('GIDbasedlv').insert(supabase_data).execute()
                    logger.info(f"✅ Inserted new pastebin data for user: {user_id}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            except Exception as e:
                logger.error(f"❌ Save error: {type(e).__name__}: {str(e)}", exc_info=True)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        super().do_POST()

def start_server():
    """Start the HTTP server"""
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        url = f"http://0.0.0.0:{PORT}/"

        print("=" * 60)
        print("LangGames - Production Server")
        print("=" * 60)
        print(f"Server URL: {url}")
        print(f"Port: {PORT}")

        if supabase_client:
            print(f"Database: ✓ Encrypted pastebin connected")
        else:
            print(f"Database: ✗ Not configured")

        print("")
        print("Server is ready and listening for requests...")
        print("=" * 60)
        print("")

        # Start server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("Shutting down server...")
            print("=" * 60)
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
