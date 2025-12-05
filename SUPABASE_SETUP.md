# Supabase Setup Guide for LangGames

## Environment Variables

Add these variables to your `.env` file:

```env
SUPABASE_PUBLIC_URI=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-service-role-key-here
```

**Note:** The old `KEY` variable for local encryption is no longer needed as LangGames now uses Supabase exclusively for data storage.

## Table Structure

Create a table named `GIDbasedLV` in your Supabase project with the following structure:

### SQL Schema

```sql
CREATE TABLE GIDbasedLV (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  level INTEGER DEFAULT 0,
  score INTEGER DEFAULT 0,
  highScore INTEGER DEFAULT 0,
  gamesPlayed INTEGER DEFAULT 0,
  stats JSONB DEFAULT '{}'::jsonb,
  lastPlayed TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster user_id lookups
CREATE INDEX idx_gidbasedlv_user_id ON GIDbasedLV(user_id);

-- Create index for sorting by updated_at
CREATE INDEX idx_gidbasedlv_updated_at ON GIDbasedLV(updated_at DESC);
```

### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `user_id` | TEXT | User identifier (email from WalkerAuth or custom ID) |
| `level` | INTEGER | Current game level |
| `score` | INTEGER | Current score |
| `highScore` | INTEGER | Highest score achieved |
| `gamesPlayed` | INTEGER | Total number of games played |
| `stats` | JSONB | Additional statistics (totalScore, levelsCompleted, etc.) |
| `lastPlayed` | TEXT | ISO timestamp of last play session |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Record last update time |

## Row Level Security (RLS) - Optional

If you want to enable RLS for better security:

```sql
-- Enable RLS
ALTER TABLE GIDbasedLV ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to read their own data
CREATE POLICY "Users can read own data"
  ON GIDbasedLV
  FOR SELECT
  USING (true);  -- Allow all for now, or use auth.uid() if you integrate Supabase Auth

-- Policy to allow users to insert their own data
CREATE POLICY "Users can insert own data"
  ON GIDbasedLV
  FOR INSERT
  WITH CHECK (true);  -- Allow all for now

-- Policy to allow users to update their own data
CREATE POLICY "Users can update own data"
  ON GIDbasedLV
  FOR UPDATE
  USING (true);  -- Allow all for now
```

## How It Works

1. **Save Data**: When the game saves, it:
   - Gets `user_id` from localStorage (user's email from WalkerAuth or 'default_user')
   - Sends game data to `/api/data/save` endpoint
   - Backend checks if a record exists for that `user_id`
   - If exists: updates the record
   - If not: inserts a new record
   - All saves go directly to Supabase (no local storage)

2. **Load Data**: When the game loads, it:
   - Gets `user_id` from localStorage
   - Requests data from `/api/data/load?user_id=<user_id>`
   - Backend queries Supabase for the most recent save for that user
   - Returns empty data if no save exists for that user

3. **Auto-Save**: The game automatically saves to Supabase every 30 seconds while playing.

## Testing

1. Add your Supabase credentials to `.env`
2. Run the game: `python3 LangGames.py`
3. Play the game and the data should automatically sync to Supabase
4. Check your Supabase dashboard to see the saved data in the `GIDbasedLV` table

## Notes

- **Supabase is required**: The game will not save data without Supabase credentials configured
- The `user_id` field uses the email from WalkerAuth if the user is logged in
- If not logged in, it uses 'default_user' as the identifier
- The system automatically handles both INSERT and UPDATE operations
- All game data is stored exclusively in Supabase (no local file storage)

## Migration from Old Version

If you previously used the EMDATA.txt file-based storage:
- Your old save data will **not** be automatically migrated
- You can manually create a record in Supabase if you need to preserve old saves
- The `encryption_manager.py` module is no longer used
