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

## 🚀 Access & Play

### Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for WalkerAuth and Supabase)
- WalkerAuth account (free registration)

### How to Access

Visit the deployed game at your hosting URL and sign in with WalkerAuth to start playing!

## 🗂️ File Structure

```
LangFight/
├── src/                      # Game files
│   ├── index.html           # Game UI and tutorial
│   ├── game.js              # Core game logic & click-to-match
│   ├── vocabulary.js        # Kannada vocabulary database
│   ├── style.css            # Game styles & tutorial CSS
│   └── Map.png              # Path background image
└── README.md                # This file
```

## ⚙️ Backend Configuration

### Server API

The game automatically uses the current domain for API calls via dynamic routing.

### Supabase Database

**Required Table Schema:**
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

This table stores all player progress linked to their WalkerAuth account.

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

### Data not saving
- Open browser console (F12) and check for errors
- Verify you're logged in with WalkerAuth
- Check that Supabase connection is working
- Ensure internet connection is stable

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
- Try refreshing the page

### Vehicles moving too fast/slow
- Use the **Speed Slider** in-game (1x-5x)
- First 3 levels intentionally slower for beginners
- Adjust speed in real-time while playing

### Game not loading
- Check internet connection
- Clear browser cache
- Try a different browser
- Disable browser extensions that might interfere
- Check browser console (F12) for error messages

## 🔒 Security Notes

- WalkerAuth handles secure authentication
- User data isolated per account in Supabase
- All API calls authenticated via user tokens
- No sensitive data stored in browser localStorage
- HTTPS encryption for all network requests
- Data privacy: only you can access your game progress

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
4. Test thoroughly in browser
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

## 🚀 Deployment

The game can be deployed on any static hosting service or platform that supports Python web servers.

### Deployment Options

**Recommended Platforms:**
- Railway
- Render
- Heroku
- DigitalOcean
- AWS
- Google Cloud Platform

See deployment guides in the repository:
- `DEPLOY_RAILWAY.md` - Railway deployment instructions
- `DEPLOY_FREE.md` - Free hosting options

### Environment Variables Required

Configure these in your hosting platform:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

## 📚 Additional Documentation

For detailed setup and deployment instructions, see:
- **WalkerAuth Integration**: `WALKERAUTH_INTEGRATION.md`
- **Supabase Setup**: `SUPABASE_SETUP.md`
- **Railway Deployment**: `DEPLOY_RAILWAY.md`
- **Free Hosting Options**: `DEPLOY_FREE.md`

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
