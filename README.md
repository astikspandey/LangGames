# LangFight - Kannada Learning Game

An interactive educational game to learn Kannada vocabulary through drag-and-drop gameplay with particle effects and audio feedback.

## ✨ Key Features

- **🎮 Web Trial + Local Full Version** - Try 6 levels online, download for unlimited access
- **🔒 Encrypted Storage** - XOR encryption with custom keys (EMDATA.txt + .env)
- **💾 Auto-Save/Load** - Progress automatically saved and restored
- **☁️ Auto-Sync** - Optional automatic cloud backup (enabled by default to local server)
- **🎵 Audio & Visual Feedback** - Particle explosions and sound effects
- **📥 Export/Import** - Backup and restore your encrypted save files
- **📱 Offline Full Version** - Run locally without internet

## Game Mechanics

### Visual & Audio Feedback
- **✅ Correct matches**: Green particle explosion + ascending chime
- **❌ Wrong matches**: Red X indicator + descending error tone
- **Real-time feedback**: Immediate response to every action

### Progressive Difficulty
- **Levels 1-2**: Letters (ಅ, ಇ, ಉ, etc.)
- **Levels 3-5**: Words (Water, Food, House, etc.)
- **Levels 6+**: Sentences (How are you?, Thank you, etc.)

### Multiple Vehicle Types
- 🟢 **Green SUVs** (fast) - Letters
- 🟠 **Orange Tanks** (medium) - Words
- 🟣 **Purple Blimps** (slow) - Sentences

## Features

### Full Desktop Version (GitHub Clone)
When you run `python3 LangFight.py`, you get:
- **Unlimited Levels** - Access all content (letters, words, sentences)
- **Encrypted Data Storage** - EMDATA.txt with custom KEY in .env
- **Auto-Save** - Saves every 30 seconds + on browser close
- **Auto-Load** - Restores progress with "Welcome Back!" message
- **Auto-Sync** - Syncs to local server automatically (configurable)
- **Persistent Stats** - High scores, games played, total score
- **Export/Import** - Backup encrypted save files
- **Browser Fallback** - Works offline with browser localStorage

## Installation & Running

### Requirements
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Quick Start

**⭐ Recommended: Direct Full Version**
```bash
python3 LangFight.py
# Opens game directly with ?full=true (unlimited levels)
```

This launches:
- Full version with unlimited levels
- Auto-save and auto-load functionality
- Encrypted data storage (EMDATA.txt)
- Local HTTP server on port 9050
- Sync server at `/server/save` and `/server/load`

### Access Full Version

**Direct launch** (Only way for GitHub clone)
```bash
python3 LangFight.py
# Opens full version with unlimited levels
```

## Server Architecture

The Python launcher (`LangFight.py`) starts a local HTTP server on port 9050.

### Routes (Port 9050)

**Main Route:**
- `/` - Full version game (unlimited levels)

**Sync Endpoints:**
- `/server/save` - Save encrypted game data (POST)
- `/server/load` - Load encrypted game data (GET)

**API Endpoints:**
- `/api/data/save` - Save game data (POST)
- `/api/data/load` - Load game data (GET)
- `/api/sync/settings` - Configure sync settings (GET/POST)

### Default Sync Configuration

By default, the full version auto-syncs to the local server:
- **Default URL**: `http://localhost:9050/server/save`
- **Auto-sync**: Enabled by default
- **Customizable**: Change in-game (💾 Data → ⚙️ Sync Settings)

**To change default sync URL**, edit `LangFight.py` or use environment variable:
```bash
export SYNC_URL=https://your-server.com/api/save
python3 LangFight.py
```

## Data Storage & Encryption

### Server-Side Encryption (Full Version)

1. **Encryption Key** (`.env` file):
   - Generated on first run: 64-character hex key
   - Stored in project root as `KEY=...`
   - Used for all encryption/decryption

2. **Encrypted Data** (`EMDATA.txt`):
   - Stores: Level, Score, High Score, Games Played, Stats, Last Played
   - Encrypted using XOR encryption with your KEY
   - Saved automatically on exit and periodically during play

3. **Auto-Save Triggers** (Full Version Only):
   - Every 30 seconds during gameplay
   - When browser tab/window closes
   - When server shuts down (Ctrl+C)
   - On game over

4. **Auto-Load on Startup**:
   - Server displays saved game info on startup
   - Game automatically loads and restores progress
   - Shows "Welcome Back! Level X • Score: Y" message

### Browser Fallback Storage

If server is unavailable:
- Falls back to browser's localStorage
- Uses `crypto.js` for browser-based encryption
- Data stored as `EMDATA` in localStorage
- Encryption key stored as `ENCRYPTION_KEY`

### Data Management

Click **💾 Data** button in-game to:
1. **📥 Export EMDATA.txt** - Download encrypted save file
2. **📤 Import EMDATA.txt** - Upload backup save file
3. **🔑 Export .env Key** - Download encryption key
4. **⚙️ Sync Settings** - Configure auto-sync URL and enable/disable

### Cloud Sync

**Auto-Sync (Enabled by Default):**
- Automatically syncs to `http://localhost:9050/server/save`
- Triggered after every save operation
- Uses curl subprocess in background
- Change URL in sync settings or `mainsite/server.py`

**Manual Sync:**
```bash
# Using provided script
chmod +x sync_data.sh
./sync_data.sh https://your-server.com/api/save

# Or use curl directly
curl -X POST https://your-server.com/api/save \
  -H "Content-Type: application/json" \
  -d @EMDATA.txt
```

**Configure Sync in Game:**
1. Click 💾 Data → ⚙️ Sync Settings
2. Enter your server URL
3. Enable/disable auto-sync
4. Click Save

## Game Controls

- **Drag and Drop**: Drag Kannada words to matching vehicles
- **CPU Mode**: Auto-play (Password: `abc123`)
- **Speed Control**: Adjust game speed (⚡ button)
- **Level Skip**: Jump to levels (📊 button)
- **Fullscreen**: Press `*` key
- **Data Menu**: Save/load management (💾 button)

## File Structure

```
LangFight/
├── LangFight.py              # 🌟 Main launcher (starts server + opens game)
├── encryption_manager.py     # Server-side encryption handler
├── .env                      # Encryption key (auto-generated)
├── EMDATA.txt                # Encrypted save data (auto-created)
├── sync_settings.json        # Sync configuration (auto-created)
├── sync_data.sh              # Manual cloud sync script
├── src/                      # Game files
│   ├── index.html           # Game UI
│   ├── game.js              # Core game logic ⚙️ CONFIG at top
│   ├── crypto.js            # Browser-side encryption
│   ├── vocabulary.js        # Kannada vocabulary database
│   ├── style.css            # Game styles
│   └── Map.png              # Path background image
├── .gitignore               # Protects .env and EMDATA.txt
└── README.md                # This file
```

## Configuration

### Easy Configuration Points

The game has a config section at the top of `src/game.js`:

**`src/game.js`** (Lines 1-6):
```javascript
// ============================================================
// CONFIGURATION - Easy to modify
// ============================================================
const SERVER_PORT = 9050;  // Change this to match your server port
const SERVER_URL = `http://localhost:${SERVER_PORT}`;
// ============================================================
```

### Change Port

1. Edit `src/game.js` → Change `SERVER_PORT = 9050`
2. Edit `LangFight.py` → Change `PORT = 9050`
3. Restart

### Change Sync Server

**Method 1: Environment variable** (Recommended)
```bash
export SYNC_URL=https://your-server.com/api/save
python3 LangFight.py
```

**Method 2: In-game settings** (Per user)
- Click 💾 Data → ⚙️ Sync Settings
- Enter URL and save

## Server Startup Info

When you run `python3 LangFight.py`, the console shows:

```
============================================================
🎮 LangFight - Kannada Learning Game
============================================================
Server: http://localhost:9050/
Sync Endpoint: http://localhost:9050/server/save
Encryption: ✓ Key loaded
Sync: ✓ Enabled (local server)

Saved Game: ✓ Found (Level 5, Score 1230)

Features:
  ✓ Full version with unlimited levels
  ✓ Encrypted data storage (EMDATA.txt)
  ✓ Auto-save every 30s + on exit
  ✓ Auto-load on startup
  ✓ Sync server at /server/save

Press Ctrl+C to stop the server
============================================================
```

## Customization

### Change Vocabulary
Edit `src/vocabulary.js`:
```javascript
levels: {
  1: [
    { english: 'A', kannada: 'ಅ', difficulty: 'letter' },
    // Add more...
  ]
}
```

### Change Colors/Styles
Edit `src/style.css` for visual customization

### Change Vehicle Colors
Edit `src/game.js` in the `Tank` class:
```javascript
getColor() {
  switch (this.vehicleType) {
    case 'suv': return '#4CAF50';      // Green
    case 'tank': return '#FF9800';     // Orange
    case 'blimp': return '#9C27B0';    // Purple
  }
}
```

## Troubleshooting

### Game won't start
```bash
# Make sure you're in the LangFight directory
cd /path/to/LangFight

# Launch the game
python3 LangFight.py
```

### Port already in use
```bash
# Kill process on port 9050
lsof -ti:9050 | xargs kill -9

# Or change the port in both files (see Configuration section)
```

### Data not saving
- Check you're using full version (`python3 LangFight.py`)
- Open browser console (F12) and check for errors
- Verify .env file exists with KEY=...
- Check EMDATA.txt was created in project root

### Lost encryption key
1. If you have backup .env file, restore it to project root
2. If not, you'll need to start fresh (old data can't be decrypted)
3. **Prevention**: Regularly export your .env key (💾 Data → 🔑 Export .env)

### Can't import EMDATA.txt
- Ensure .env file has the correct KEY
- Verify EMDATA.txt is valid (exported from same game)
- Check file isn't corrupted
- Try exporting again from working installation

### Sync not working
- Check server is running (`python3 LangFight.py`)
- Verify sync URL in settings (💾 Data → ⚙️ Sync Settings)
- Check server console for error messages
- Test endpoint: `curl http://localhost:9050/server/load`

### Welcome back message not showing
- Check EMDATA.txt exists with data
- Open browser console (F12) for errors
- Verify server loaded the data (check server console on startup)
- Ensure server is running (`python3 LangFight.py`)

## Development

### Architecture

**Hybrid Client-Server:**
- **Frontend**: Pure HTML/CSS/JavaScript (no build step)
- **Backend**: Python HTTP server (optional, for sync and serving)
- **Storage**: File-based (EMDATA.txt) + browser localStorage fallback
- **Encryption**: XOR encryption (server) + browser crypto (fallback)

### Testing Locally

**Test server:**
```bash
python3 LangFight.py
# Visit http://localhost:9050
```

**Test encryption:**
```bash
python3 -c "from encryption_manager import EncryptionManager; \
  em = EncryptionManager(); em.load_or_create_key(); \
  print('Key:', em.key[:20] + '...')"
```

**Test endpoints:**
```bash
# Check server is running
curl http://localhost:9050/server/load

# Save test data
curl -X POST http://localhost:9050/server/save \
  -H "Content-Type: application/json" \
  -d '{"level":5,"score":1000}'
```

### Making Changes

- **Edit vocabulary**: `src/vocabulary.js`
- **Modify game logic**: `src/game.js`
- **Change server**: `LangFight.py`
- **Update encryption**: `encryption_manager.py` or `src/crypto.js`
- **Modify styles**: `src/style.css`
- **No build required** - just refresh browser!

### Adding New Endpoints

Edit `LangFight.py` to add custom server routes:
```python
# In the CustomHTTPRequestHandler class
# Add to do_GET method for GET requests
# Add to do_POST method for POST requests
```

## Security Notes

- **Encryption key** stored in `.env` file - keep it safe!
- **.gitignore** protects `.env` and `EMDATA.txt` from commits
- Data encrypted before upload - server sees only ciphertext
- XOR encryption is simple but effective for local use
- **Export .env regularly** as backup (💾 Data → 🔑 Export .env)
- If .env is lost, encrypted data cannot be recovered

## Contributing

Feel free to:
- Add more vocabulary to `src/vocabulary.js`
- Improve encryption in `encryption_manager.py`
- Enhance UI in `src/style.css`
- Fix bugs and submit pull requests

## License

Educational project - MIT License
Feel free to modify and distribute

## Credits

Created with Claude Code
Kannada language learning game
Made with ❤️ for language learners
