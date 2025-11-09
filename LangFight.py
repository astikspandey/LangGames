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

from encryption_manager import EncryptionManager
from walkerauth_client import WalkerAuthClient

PORT = int(os.getenv('PORT', '9048'))
HOST = os.getenv('HOST', '0.0.0.0')

# WalkerAuth Configuration
WALKERAUTH_SECRET_KEY = "langgames_secret_key_12345"
walkerauth_client = WalkerAuthClient(WALKERAUTH_SECRET_KEY)

# Initialize encryption manager
encryption_manager = EncryptionManager()
encryption_manager.load_or_create_key()

# Sync settings file
SYNC_SETTINGS_FILE = "sync_settings.json"

def load_sync_settings():
    """Load sync settings from file"""
    if os.path.exists(SYNC_SETTINGS_FILE):
        try:
            with open(SYNC_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass

    # Auto-sync enabled by default with environment variable URL
    default_url = os.getenv('SYNC_URL', 'https://example.com/api/save')
    default_settings = {"enabled": True, "url": default_url}

    # Save default settings
    save_sync_settings(default_settings)

    return default_settings

def save_sync_settings(settings):
    """Save sync settings to file"""
    with open(SYNC_SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

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
        if self.path == '/api/sync/settings':
            # Get sync settings
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            settings = load_sync_settings()
            self.wfile.write(json.dumps(settings).encode())
            return

        elif self.path == '/api/data/load':
            # Load encrypted data
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = encryption_manager.load_encrypted_data()
            self.wfile.write(json.dumps(data if data else {}).encode())
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

        # Handle sync settings update
        if self.path == '/api/sync/settings':
            try:
                settings = json.loads(post_data.decode())
                save_sync_settings(settings)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())

                if settings.get('enabled'):
                    print(f"\n✓ Sync enabled to: {settings.get('url')}")
                else:
                    print("\n✗ Sync disabled")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        # Handle save data request
        elif self.path == '/api/data/save':
            try:
                data = json.loads(post_data.decode())

                # Save encrypted data locally
                encryption_manager.save_encrypted_data(data)

                # Sync to remote if enabled
                settings = load_sync_settings()
                if settings.get('enabled') and settings.get('url'):
                    threading.Thread(
                        target=self.sync_to_remote,
                        args=(settings['url'],),
                        daemon=True
                    ).start()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        super().do_POST()

    def sync_to_remote(self, upload_url):
        """Sync encrypted data to remote server using curl"""
        try:
            # Read encrypted data from file
            with open('EMDATA.txt', 'r') as f:
                encrypted_data = f.read()

            # Create JSON payload
            payload = json.dumps({'data': encrypted_data})

            # Use curl to upload
            result = subprocess.run(
                ['curl', '-X', 'POST', upload_url,
                 '-H', 'Content-Type: application/json',
                 '-d', payload,
                 '-s', '-w', '\n%{http_code}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                http_code = lines[-1] if lines else '0'

                if http_code == '200':
                    print(f"✓ Data synced to {upload_url}")
                else:
                    # Only show error if it's not the default example URL
                    if upload_url != 'https://example.com/api/save':
                        print(f"✗ Sync failed (HTTP {http_code})")
            else:
                if upload_url != 'https://example.com/api/save':
                    print(f"✗ Sync error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✗ Sync timeout")
        except Exception as e:
            print(f"✗ Sync error: {e}")

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
        print(f"Encryption: {'✓ Key loaded' if encryption_manager.key else '✗ No key'}")

        settings = load_sync_settings()
        sync_url = settings.get('url', 'https://example.com/api/save')

        if settings.get('enabled'):
            if sync_url != 'https://example.com/api/save':
                print(f"Sync: ✓ Auto-sync enabled → {sync_url}")
            else:
                print(f"Sync: ⚠ Enabled but needs URL (💾 Data → ⚙️ Sync Settings)")
        else:
            print(f"Sync: ✗ Disabled")

        print("")
        print("Features:")
        print("  ✓ Local HTTP server for game")
        print("  ✓ Encrypted data storage (EMDATA.txt)")
        print("  ✓ Automatic cloud sync (when enabled)")
        print("  ✓ Export/Import save files")
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

            # Check if EMDATA.txt exists and show status
            if os.path.exists('EMDATA.txt'):
                file_size = os.path.getsize('EMDATA.txt')
                print(f"✓ Game data saved: EMDATA.txt ({file_size} bytes)")
            else:
                print("ℹ No game data saved yet")

            print("Goodbye!")
            print("=" * 60)

            httpd.shutdown()

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    start_server()
