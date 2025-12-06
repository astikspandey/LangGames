#!/usr/bin/env python3
import os
import sys
import subprocess

# Check if running in virtual environment
def is_venv():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

# Setup virtual environment if needed
def setup_venv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, 'venv')

    if not is_venv():
        print("Setting up virtual environment...")

        # Create venv if it doesn't exist
        if not os.path.exists(venv_dir):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)

        # Determine venv python path
        if sys.platform == 'win32':
            venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(venv_dir, 'bin', 'python3')

        # Install dependencies
        print("Installing dependencies...")
        requirements = ['pycryptodome', 'requests']
        subprocess.run([venv_python, '-m', 'pip', 'install', '--quiet'] + requirements, check=True)

        # Re-execute script in venv
        print("Restarting in virtual environment...\n")
        os.execv(venv_python, [venv_python] + sys.argv)

# Run venv setup before any other imports
if __name__ == "__main__":
    setup_venv()

import http.server
import socketserver
import webbrowser
import time
import threading
import json

USE_PYNPUT = os.getenv('DISABLE_PYNPUT', '0') != '1'
Controller = None
Key = None

if USE_PYNPUT:
    try:
        from pynput.keyboard import Controller, Key
    except ImportError:
        # In headless/containerized environments this may fail or be undesirable
        print("pynput not available; fullscreen auto-toggle disabled")
        Controller = None
        Key = None
else:
    print("pynput disabled by DISABLE_PYNPUT=1; fullscreen auto-toggle disabled")

from walkerauth_client import WalkerAuthClient

# Import pastebin client (replaces Supabase)
try:
    from pastebin_client import create_pastebin_client
    PASTEBIN_AVAILABLE = True
except ImportError:
    PASTEBIN_AVAILABLE = False
    print("Warning: Pastebin client not available")

PORT = int(os.getenv('PORT', '2937'))
HOST = os.getenv('HOST', '0.0.0.0')

# WalkerAuth Configuration
WALKERAUTH_SECRET_KEY = "langgames_secret_key_12345"
walkerauth_client = WalkerAuthClient(WALKERAUTH_SECRET_KEY)

# Initialize pastebin client (replaces Supabase)
supabase_client = None  # Keep name for compatibility

def load_pastebin_credentials():
    """Load pastebin credentials from .env file"""
    env_path = ".env"
    pastebin_url = None
    site_id = None
    secret_key = None

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('PASTEBIN_URL='):
                    pastebin_url = line.split('=', 1)[1]
                elif line.startswith('SITE_ID='):
                    site_id = line.split('=', 1)[1]
                elif line.startswith('SECRET_KEY='):
                    secret_key = line.split('=', 1)[1]

    return pastebin_url, site_id, secret_key

def init_pastebin():
    """Initialize pastebin client"""
    global supabase_client  # Keep name for compatibility

    if not PASTEBIN_AVAILABLE:
        print("✗ Pastebin client not available")
        return None

    pastebin_url, site_id, secret_key = load_pastebin_credentials()

    if pastebin_url and site_id and secret_key:
        try:
            supabase_client = create_pastebin_client(pastebin_url, site_id, secret_key)
            print(f"✓ Encrypted pastebin connected: {pastebin_url}")
            print(f"  Site ID: {site_id}")
            return supabase_client
        except Exception as e:
            print(f"✗ Pastebin connection failed: {e}")
            return None
    else:
        print("ℹ Pastebin credentials not found in .env")
        print("  Required: PASTEBIN_URL, SITE_ID, SECRET_KEY")
        return None

# Initialize pastebin on startup
init_pastebin()

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
        if self.path == '/api/data/load':
            # Load data from Supabase only
            try:
                if not supabase_client:
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

                # Query Supabase
                result = supabase_client.table('GIDbasedLV').select('*').eq('user_id', user_id).order('updated_at', desc=True).limit(1).execute()

                if result.data and len(result.data) > 0:
                    # Use the most recent save
                    data = result.data[0]
                    print(f"✓ Loaded data from Supabase for user: {user_id}")
                else:
                    print(f"ℹ No data found for user: {user_id}")
                    data = {}

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                print(f"✗ Supabase load error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif self.path.startswith('/auth/success'):
            # Handle WalkerAuth success redirect
            # Parse query parameters
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
        // Store user data in localStorage
        localStorage.setItem('walkerauth_token', '{token}');
        localStorage.setItem('user_email', '{user_data.get('email', '')}');
        localStorage.setItem('user_name', '{user_data.get('username', '')}');
        localStorage.setItem('user_avatar', '{user_data.get('profilePictureUrl', '')}');

        // Redirect to game after 2 seconds
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

                print(f"\n📝 Received OAuth callback from {site_id}")

                # Decrypt user data
                user_data = walkerauth_client.decrypt_user_data(encrypted, iv)

                if not user_data:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Failed to decrypt user data"}).encode())
                    return

                print(f"✓ Authenticated user: {user_data.get('username')} ({user_data.get('email')})")

                # Generate session token
                token = walkerauth_client.generate_session_token(user_data)
                print(f"✓ Session token generated: {token[:20]}...")

                # Return success with token
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "token": token}).encode())

            except Exception as e:
                print(f"✗ Error in OAuth callback: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        # Handle save data request
        if self.path == '/api/data/save':
            try:
                data = json.loads(post_data.decode())

                # Save to database (encrypted pastebin)
                if not supabase_client:
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

                # Check if record exists
                existing = supabase_client.table('GIDbasedLV').select('id').eq('user_id', user_id).execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing record
                    result = supabase_client.table('GIDbasedLV').update(supabase_data).eq('user_id', user_id).execute()
                    print(f"✓ Updated Supabase data for user: {user_id}")
                else:
                    # Insert new record
                    result = supabase_client.table('GIDbasedLV').insert(supabase_data).execute()
                    print(f"✓ Inserted new Supabase data for user: {user_id}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            except Exception as e:
                print(f"✗ Supabase save error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        super().do_POST()

def press_asterisk():
    """Wait 0.6 seconds and press the * key if supported"""
    if Controller is None:
        return
    time.sleep(0.6)
    keyboard = Controller()
    keyboard.press('*')
    keyboard.release('*')
    print("Pressed * key to toggle fullscreen")

def start_server():
    """Start the HTTP server"""
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        url = f"http://{HOST}:{PORT}/"

        print("=" * 60)
        print("LangGames - Local Game Server")
        print("=" * 60)
        print(f"Server: {url}")

        if supabase_client:
            print(f"Database: ✓ Encrypted pastebin connected")
        else:
            print(f"Database: ✗ Not configured (add PASTEBIN_URL, SITE_ID, SECRET_KEY to .env)")

        print("")
        print("Features:")
        print("  ✓ Local HTTP server for game")
        print("  ✓ Cloud data storage via Supabase")
        print("  ✓ WalkerAuth OAuth integration")
        if Controller is None:
            print("  ℹ Fullscreen auto-toggle disabled")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        print("")

        # Open browser only if binding to localhost
        if HOST in ("127.0.0.1", "localhost"):
            webbrowser.open(url)

        # Start thread to press * after delay (only if supported)
        if Controller is not None:
            asterisk_thread = threading.Thread(target=press_asterisk, daemon=True)
            asterisk_thread.start()

        # Start server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("Shutting down server...")
            print("✓ Game data is saved in Supabase")
            print("Goodbye!")
            print("=" * 60)

            httpd.shutdown()

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    start_server()
