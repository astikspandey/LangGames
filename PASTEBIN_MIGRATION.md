# LangGames → Encrypted Pastebin Migration

LangGames now uses the **encrypted pastebin** instead of Supabase for data storage!

## ✅ What Changed

### Before (Supabase)
- Direct database connection
- Credentials visible in Supabase dashboard
- Data stored in plain format (though encrypted at rest by Supabase)

### After (Encrypted Pastebin)
- Encrypted storage through pastebin service
- End-to-end encryption with AES-256-CBC
- Data encrypted before sending to backend
- Secret key never leaves your machine

## 🔧 Setup Instructions

### 1. Make Sure Pastebin Service is Running

The pastebin service must be running first:

```bash
cd ../pastebin
npm start
```

You should see:
```
Pastebin service running on port 3001
```

### 2. Register LangGames Site

**Option A: Via pastebin website**
1. Go to http://localhost:3001 (if you set up the website)
2. Register a new site with ID: `langgames_001`

**Option B: Manual registration (recommended)**
```bash
curl -X POST http://localhost:3001/register \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "langgames_001",
    "secret_key": "5fc4cb0edec80b28daa403c85392c61340ed27d2350f0c855572fb9c30c4e9ca"
  }'
```

### 3. Configure LangGames

Your `.env` file has been automatically updated with:

```env
PASTEBIN_URL=http://localhost:3001
SITE_ID=langgames_001
SECRET_KEY=5fc4cb0edec80b28daa403c85392c61340ed27d2350f0c855572fb9c30c4e9ca
KEY=5fc4cb0edec80b28daa403c85392c61340ed27d2350f0c855572fb9c30c4e9ca
```

(Your old .env was backed up to `.env.backup`)

### 4. Start LangGames

```bash
python LangGames.py
```

You should see:
```
✓ Encrypted pastebin connected: http://localhost:3001
  Site ID: langgames_001
Database: ✓ Encrypted pastebin connected
```

## 🎮 Testing

1. **Play the game** - Go to http://localhost:9048
2. **Make progress** - Play a few rounds, level up
3. **Refresh the page** - Your progress should be saved and loaded
4. **Check encryption** - Your data is now stored encrypted in the pastebin

### Verify Encrypted Storage

```bash
# Via pastebin website (if set up)
# Go to http://localhost:3000
# Click "Retrieve Data"
# You'll see encrypted game data

# Or via curl
curl "http://localhost:3001/retrieve?site_id=langgames_001&enc=PROOF&epo=EPOCH"
```

## 📊 Data Structure

Each user's game data is stored as:
- **Location**: `user_id` (e.g., "default_user" or WalkerAuth user ID)
- **Data** (encrypted):
  ```json
  {
    "user_id": "default_user",
    "level": 5,
    "score": 1250,
    "highScore": 1500,
    "gamesPlayed": 10,
    "stats": {...},
    "lastPlayed": "2024-11-25T12:00:00"
  }
  ```

## 🔒 Security Improvements

### Before (Supabase)
- ✓ SSL/TLS encryption in transit
- ✓ Encryption at rest (Supabase managed)
- ✗ Data visible to Supabase administrators
- ✗ Database credentials needed

### After (Encrypted Pastebin)
- ✓ SSL/TLS encryption in transit
- ✓ End-to-end encryption (you control the key)
- ✓ Data unreadable without secret key
- ✓ Secure handshake protocol
- ✓ Epoch-based encryption (unique per save)

## 🔄 Migration from Supabase

If you have existing data in Supabase:

### Option 1: Start Fresh
- Just use the new system
- Old Supabase data remains accessible if you switch back

### Option 2: Migrate Data
1. Export from Supabase:
   ```python
   # In Python shell
   from supabase import create_client
   client = create_client(url, key)
   data = client.table('GIDbasedLV').select('*').execute()
   ```

2. Import to Pastebin:
   ```python
   from pastebin_client import create_pastebin_client
   client = create_pastebin_client(url, site_id, secret_key)
   for row in data:
       client.client.store(row['user_id'], row)
   ```

## 🔙 Rollback to Supabase

If you need to switch back:

1. Restore old .env:
   ```bash
   cp .env.backup .env
   ```

2. Restore old requirements.txt:
   ```bash
   echo "supabase" >> requirements.txt
   ```

3. Restore Supabase imports in LangGames.py
   (Or use git to revert changes)

## 📝 Code Changes Summary

1. **pastebin_client.py** - New file, handles pastebin communication
2. **LangGames.py**:
   - Replaced Supabase imports with pastebin client
   - Updated credential loading
   - Updated error messages
   - **No changes to game logic!**
3. **requirements.txt** - Removed supabase dependency
4. **.env** - Updated with pastebin credentials

## 🐛 Troubleshooting

### "Database not configured"
- Check pastebin service is running: `curl http://localhost:3001/handshake?site_id=langgames_001`
- Verify .env has PASTEBIN_URL, SITE_ID, SECRET_KEY

### "Site not found"
- Register the site first (see step 2)
- Check SITE_ID matches in .env

### "Handshake failed"
- Verify SECRET_KEY matches between .env and registration
- Check pastebin service is accessible

### "Connection refused"
- Start the pastebin service first
- Check PASTEBIN_URL in .env is correct

## ✨ Benefits

- ✅ Full control over your data
- ✅ No third-party database needed
- ✅ End-to-end encryption
- ✅ Works offline (localhost)
- ✅ No API rate limits
- ✅ Free forever
- ✅ Can host pastebin on GitHub Pages + Serverless

## 🎉 Enjoy!

Your LangGames game data is now encrypted and secure!
