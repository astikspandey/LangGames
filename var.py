#!/usr/bin/env python3
"""
Configuration file for LangFight
Contains all URLs and configuration variables
"""

# Server Configuration
import os
SERVER_HOST = os.getenv('HOST', 'localhost')
SERVER_PORT = int(os.getenv('PORT', 9048))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# API Endpoints
API_BASE_URL = f"{SERVER_URL}/api"
API_DATA_SAVE = f"{API_BASE_URL}/data/save"
API_DATA_LOAD = f"{API_BASE_URL}/data/load"
API_SYNC_SETTINGS = f"{API_BASE_URL}/sync/settings"

# Authentication URLs (to be configured)
WALKER_AUTH_URL = ""  # WalkerAuth server URL - to be provided
WALKER_AUTH_LOGIN = f"{WALKER_AUTH_URL}/login" if WALKER_AUTH_URL else ""
WALKER_AUTH_LOGOUT = f"{WALKER_AUTH_URL}/logout" if WALKER_AUTH_URL else ""
WALKER_AUTH_VERIFY = f"{WALKER_AUTH_URL}/verify" if WALKER_AUTH_URL else ""

# Pastebin URLs (to be configured)
PASTEBIN_URL = ""  # Pastebin server URL - to be provided
PASTEBIN_SAVE = f"{PASTEBIN_URL}/save" if PASTEBIN_URL else ""
PASTEBIN_LOAD = f"{PASTEBIN_URL}/load" if PASTEBIN_URL else ""

# Sync Configuration
DEFAULT_SYNC_URL = "https://example.com/api/save"  # Default sync URL (placeholder)
SYNC_SETTINGS_FILE = "sync_settings.json"

# Encryption Configuration
ENCRYPTION_KEY_FILE = "secret.key"
ENCRYPTED_DATA_FILE = "EMDATA.txt"

# Feature Flags
AUTH_ENABLED = False  # Enable when WalkerAuth is configured
SYNC_ENABLED = True   # Cloud sync enabled by default
AUTO_SAVE_ENABLED = True
AUTO_SAVE_INTERVAL = 30  # seconds

# Game Configuration
TRIAL_MODE = False  # Trial mode disabled - infinite levels
MAX_LEVEL = 999  # No limit
DEFAULT_LIVES = 3
BASE_SPAWN_RATE = 3000  # milliseconds

# File Paths
SRC_DIRECTORY = "src"
STATIC_FILES = ["index.html", "game.js", "vocabulary.js", "crypto.js"]

# Environment Variables (os already imported above)
SYNC_URL_ENV = os.getenv('SYNC_URL', DEFAULT_SYNC_URL)

# Print configuration (for debugging)
def print_config():
    """Print current configuration"""
    print("=" * 60)
    print("LangFight Configuration")
    print("=" * 60)
    print(f"Server: {SERVER_URL}")
    print(f"API Base: {API_BASE_URL}")
    print(f"Auth Enabled: {AUTH_ENABLED}")
    print(f"Sync Enabled: {SYNC_ENABLED}")
    print(f"Trial Mode: {TRIAL_MODE}")
    print(f"Max Level: {'Unlimited' if MAX_LEVEL == 999 else MAX_LEVEL}")
    print("=" * 60)
    print("")
    if WALKER_AUTH_URL:
        print(f"WalkerAuth: {WALKER_AUTH_URL}")
    else:
        print("WalkerAuth: Not configured")
    if PASTEBIN_URL:
        print(f"Pastebin: {PASTEBIN_URL}")
    else:
        print("Pastebin: Not configured")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
