# LangFight - Kannada Learning Game

An interactive educational game to learn Kannada vocabulary through click-to-match gameplay with particle effects and audio feedback.

## ✨ Key Features

- **🎮 Click-to-Match Gameplay** - Simple one-click matching system
- **💾 Cloud Auto-Save** - Progress automatically saved to Supabase
- **☁️ Cross-Device Sync** - Play on any device with your account
- **🎵 Audio & Visual Feedback** - Particle explosions and sound effects
- **🔐 WalkerAuth Integration** - Secure authentication and user profiles
- **📚 Progressive Learning** - First 3 levels designed for beginners
- **🎓 Interactive Tutorial** - Guides new players through game mechanics
- **📱 Web-Based** - No installation required

## 🎮 How to Play

### Click-to-Match System
1. **Click a Kannada word** from the sidebar
2. It **automatically matches with the FIRST vehicle** on the path (the one furthest along)
3. **Correct match** → Vehicle destroyed, points earned! ✅
4. **Wrong match** → Lose a life ❌
5. Match all vehicles before they reach the end of the path!

### Learning Progression

**First 3 Levels (Learning Mode):**
- **Much slower vehicles** - More time to think and learn
- **Longer spawn delays** - One vehicle at a time to reduce pressure
- **Level 1**: Base speed 0.3, spawns every 5 seconds
- **Level 2**: Base speed 0.5, spawns every 4 seconds
- **Level 3**: Base speed 0.7, spawns every 3.5 seconds

**Level 4+:**
- Normal difficulty with progressive speed increases
- Faster spawn rates for more challenge

### Vehicle Types & Content

The game adapts vehicle types based on vocabulary difficulty:

- 🟢 **Green SUV** (Fast) - Letters (ಅ, ಇ, ಉ, etc.)
- 🟠 **Orange Tank** (Medium) - Words (Water, Food, House, etc.)
- 🟣 **Purple Blimp** (Slow) - Sentences (How are you?, Thank you, etc.)

### Interactive Tutorial

For new users (no saved data), an interactive 4-step tutorial appears:
1. **How to Play** - Click-to-match mechanics
2. **Vehicle Types** - Learn about SUVs, Tanks, and Blimps
3. **Controls** - Speed/level sliders and lives system
4. **Tips** - Hover hints, auto-save, and keyboard shortcuts

**Tutorial Features:**
- Fully skippable at any time
- Navigate with Previous/Next buttons
- Progress dots show current step
- Only shows once per browser (stores in localStorage)
- Game pauses during tutorial

## 🎛️ Game Controls

### Main Controls
- **Click Word** - Click any Kannada word to match it with the first vehicle
- **Speed Slider** - Adjust game speed from 1x to 5x
- **Level Slider** - Jump to any level (1-20)
- **Lives** - You have 3 hearts ❤️❤️❤️

### Advanced Features
- **CPU Mode** - Auto-play mode (Password: `abc123`)
- **Fullscreen** - Press `*` key to toggle fullscreen
- **Hover Hints** - Hover over Kannada words for 0.5s to see English translation

### Visual Feedback
- **✅ Correct match**: Green particle explosion + happy chime
- **❌ Wrong match**: Red X + error sound
- **✓ Matched words**: Turn green when all instances destroyed
- **Selected word**: Glows golden (if implemented for future features)

## 📊 Game Progression

### Lives System
- Start with **3 hearts** ❤️❤️❤️
- Lose a life for:
  - Wrong word match
  - Vehicle reaches the end (missed)
- Game over when all lives lost

### Scoring
- **Points per match**: 10 × current level
- **Level up**: When all vocabulary items fully matched
- **Stats tracked**:
  - Current score
  - High score
  - Total games played
  - Total score across all games
  - Levels completed

### Game Over Screen
Shows detailed feedback:
- Final score and level reached
- **Wrong Matches**: Lists what you tried vs. what was correct
- **Missed Vehicles**: Shows vehicles that reached the end
- Restart button to play again

## 💾 Data & Authentication

### Cloud Storage with Supabase

**Automatic Saving:**
- Saves every **30 seconds** during gameplay
- Saves when browser closes/tab closes
- Saves on game over
- No manual save needed!

**Data Stored:**
- Current level and score
- High score
- Games played counter
- Total score across all games
- Stats (levels completed, etc.)
- Last played timestamp

**Welcome Back System:**
- Loads your progress automatically on startup
- Shows "Welcome Back! Level X • Score: Y" for 2 seconds
- Returns you to your last level

### WalkerAuth Integration

**Authentication Features:**
- Sign in with WalkerAuth (walkerauth.walkerco.co)
- User profile displayed (avatar + name)
- Logout button in header
- Auto-login on return visits
- Data linked to your account

**First-Time Users:**
- Tutorial appears automatically
- Can skip tutorial anytime
- No data loaded (fresh start)

**Returning Users:**
- No tutorial (already completed)
- Progress loaded from Supabase
- Welcome back message shown

## 🚀 Installation & Running

### Requirements
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Supabase account (for cloud save)
- Internet connection (for WalkerAuth and Supabase)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd LangFight
```

2. **Set up environment variables**

Create a `.env` file in the project root:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

3. **Run the game**
```bash
python3 LangFight.py
```

4. **Open in browser**
- Automatically opens at `http://localhost:9048`
- Or manually visit the URL shown in console

### What Launches:
- Local HTTP server on port 9048
- Game interface with WalkerAuth login
- API endpoints for Supabase integration
- Auto-save system active

## 🗂️ File Structure

```
LangFight/
├── LangFight.py              # Main launcher (starts server)
├── walkerauth_client.py      # WalkerAuth authentication client
├── .env                      # Supabase credentials (gitignored)
├── src/                      # Game files
│   ├── index.html           # Game UI and tutorial
│   ├── game.js              # Core game logic & click-to-match
│   ├── vocabulary.js        # Kannada vocabulary database
│   ├── style.css            # Game styles & tutorial CSS
│   └── Map.png              # Path background image
├── .gitignore               # Protects .env and sensitive files
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## ⚙️ Configuration

### Server Configuration

The game automatically uses the current domain for API calls:

**`src/game.js`** (Lines 4-5):
```javascript
// Use current domain (works for both localhost and production)
const SERVER_URL = window.location.origin;
```

### Supabase Setup

1. Create a [Supabase](https://supabase.com) project
2. Create a table for game data (see schema below)
3. Get your project URL and anon key
4. Add to `.env` file

**Supabase Table Schema:**
```sql
CREATE TABLE game_data (
  user_id TEXT PRIMARY KEY,
  level INTEGER,
  score INTEGER,
  high_score INTEGER,
  games_played INTEGER,
  last_played TIMESTAMP,
  stats JSONB
);
```

### Change Port

Edit `LangFight.py`:
```python
PORT = 9048  # Change to your preferred port
```

Then update any hardcoded references if needed.

## 🎨 Customization

### Change Vocabulary

Edit `src/vocabulary.js`:
```javascript
const vocabulary = {
  levels: {
    1: [
      { english: 'A', kannada: 'ಅ', difficulty: 'letter' },
      { english: 'I', kannada: 'ಇ', difficulty: 'letter' },
      // Add more...
    ],
    2: [
      // Level 2 vocabulary...
    ]
  }
};
```

### Change Difficulty Settings

Edit `src/game.js`:

**First 3 Levels Speed:**
```javascript
getSpeed() {
  if (game.level === 1) {
    baseSpeed = 0.3; // Very slow
  } else if (game.level === 2) {
    baseSpeed = 0.5; // Slow
  } else if (game.level === 3) {
    baseSpeed = 0.7; // Still slow
  }
  // ...
}
```

**First 3 Levels Spawn Rate:**
```javascript
function startSpawning() {
  if (game.level === 1) {
    baseRate = 5000; // 5 seconds
  } else if (game.level === 2) {
    baseRate = 4000; // 4 seconds
  } else if (game.level === 3) {
    baseRate = 3500; // 3.5 seconds
  }
  // ...
}
```

### Change Colors/Styles

Edit `src/style.css`:
- Tutorial styles: Lines 641-849
- Game UI: Throughout the file
- Vehicle colors defined in `src/game.js` Tank class

### Modify Tutorial Content

Edit `src/index.html` (Lines 98-133):
```html
<div class="tutorial-step active" data-step="0">
  <h3>🎯 How to Play</h3>
  <p>Your content here...</p>
  <ul>
    <li>Step 1...</li>
    <li>Step 2...</li>
  </ul>
</div>
```

## 🐛 Troubleshooting

### Game won't start
```bash
# Make sure you're in the LangFight directory
cd /path/to/LangFight

# Check Python version
python3 --version  # Should be 3.7+

# Launch the game
python3 LangFight.py
```

### Port already in use
```bash
# Kill process on port 9048
lsof -ti:9048 | xargs kill -9

# Or change the port in LangFight.py
```

### Data not saving
- Check `.env` file has correct Supabase credentials
- Open browser console (F12) and check for errors
- Verify Supabase table exists and is accessible
- Check server console for error messages
- Test Supabase connection: `curl http://localhost:9048/api/data/load?user_id=test`

### Can't login with WalkerAuth
- Ensure internet connection is active
- Check WalkerAuth service is available
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Check browser console for errors

### Tutorial won't show
- Tutorial only shows for users with **no saved data** in Supabase
- Clear localStorage: `localStorage.removeItem('tutorialCompleted')`
- Or use a different account/browser
- Tutorial disabled if saved data exists for your account

### Welcome back message not showing
- Make sure you're logged in with WalkerAuth
- Verify data exists in Supabase for your user_id
- Check browser console (F12) for errors
- Ensure server is running: `python3 LangFight.py`

### Vehicles moving too fast/slow
- Use the **Speed Slider** in-game (1x-5x)
- For learning mode adjustments, edit speed values in `src/game.js`
- First 3 levels intentionally slower for beginners

## 🔒 Security Notes

- **Supabase credentials** stored in `.env` file - keep it safe!
- `.gitignore` protects `.env` from being committed
- WalkerAuth handles secure authentication
- User data isolated per account in Supabase
- All API calls use user_id from localStorage (set by WalkerAuth)
- No sensitive data stored in browser localStorage (only user_id, tokens)

## 🤝 Contributing

Feel free to:
- Add more vocabulary to `src/vocabulary.js`
- Enhance UI in `src/style.css`
- Improve game mechanics in `src/game.js`
- Add new tutorial steps in `src/index.html`
- Optimize difficulty progression
- Fix bugs and submit pull requests

**Development Workflow:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `python3 LangFight.py`
5. Submit a pull request

## 📜 License

Educational project - MIT License
Feel free to modify and distribute

## 🙏 Credits

Created with Claude Code
Kannada language learning game
Made with ❤️ for language learners

**Technologies Used:**
- Python 3 (HTTP server)
- Vanilla JavaScript (game logic)
- HTML5 Canvas (game rendering)
- CSS3 (styling and animations)
- Supabase (cloud database)
- WalkerAuth (authentication)

## 🐳 Docker Deployment

To run LangFight in a Docker container:

### Build the Docker Image

```bash
docker build -t langfight .
```

### Run the Docker Container

```bash
docker run -p 9048:9048 --env-file .env langfight
```

- `-p 9048:9048`: Maps port 9048 (host to container)
- `--env-file .env`: Loads Supabase credentials from .env file

### Access the Game

Open your browser at `http://localhost:9048`

### Notes
- Fullscreen auto-toggle is disabled in Docker (`DISABLE_PYNPUT=1`)
- You can still press `*` manually to toggle fullscreen
- Make sure `.env` file exists with Supabase credentials before building

## 📚 Additional Documentation

- **WalkerAuth Integration**: See `WALKERAUTH_INTEGRATION.md`
- **Supabase Setup**: See `SUPABASE_SETUP.md`
- **Deployment Guides**: See `DEPLOY_*.md` files

## 🎯 Roadmap

Future enhancements planned:
- [ ] Sound effects toggle
- [ ] More languages support
- [ ] Leaderboard system
- [ ] Achievement badges
- [ ] Daily challenges
- [ ] Mobile app version
- [ ] Multiplayer mode
- [ ] Custom vocabulary import

## 📞 Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section above
- Test in browser console (F12) for error messages
