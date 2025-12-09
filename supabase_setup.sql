-- LangGames Supabase Table Setup
-- Run this in your Supabase SQL Editor: https://app.supabase.com

-- Create the GIDbasedLV table
CREATE TABLE IF NOT EXISTS public."GIDbasedLV" (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0,
    "highScore" INTEGER DEFAULT 0,
    "gamesPlayed" INTEGER DEFAULT 0,
    stats JSONB DEFAULT '{}'::jsonb,
    "lastPlayed" TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_gidbasedlv_user_id ON public."GIDbasedLV" (user_id);

-- Create index on updated_at for sorting
CREATE INDEX IF NOT EXISTS idx_gidbasedlv_updated_at ON public."GIDbasedLV" (updated_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public."GIDbasedLV" ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can restrict this later)
CREATE POLICY "Allow all access to GIDbasedLV" ON public."GIDbasedLV"
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Grant permissions
GRANT ALL ON public."GIDbasedLV" TO anon;
GRANT ALL ON public."GIDbasedLV" TO authenticated;
GRANT USAGE ON SEQUENCE "GIDbasedLV_id_seq" TO anon;
GRANT USAGE ON SEQUENCE "GIDbasedLV_id_seq" TO authenticated;
