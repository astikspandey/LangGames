#!/usr/bin/env python3
"""
Check actual table schema in Supabase
"""
import os
from supabase import create_client

def load_credentials():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    if not url or not key:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('SUPABASE_URL='):
                        url = line.split('=', 1)[1]
                    elif line.startswith('SUPABASE_KEY='):
                        key = line.split('=', 1)[1]
    return url, key

url, key = load_credentials()
client = create_client(url, key)

print("Checking GIDbasedlv table schema...")
print("=" * 60)

# Query information_schema to get column names
try:
    # This query gets the column names from PostgreSQL's information schema
    result = client.rpc('get_columns', {
        'table_name': 'GIDbasedlv'
    }).execute()

    print("Columns in GIDbasedlv table:")
    for col in result.data:
        print(f"  - {col}")
except Exception as e:
    print(f"RPC method not available, trying direct query...")

    # Alternative: Try to get schema from a dummy insert attempt
    # Or ask user to check Supabase Table Editor
    print("\nPlease check Supabase Table Editor to see columns:")
    print("1. Go to https://app.supabase.com")
    print("2. Click Table Editor")
    print("3. Click 'GIDbasedlv' table")
    print("4. List all column names you see")
    print("\nCurrent expected columns by the code:")
    print("  - user_id (TEXT)")
    print("  - level (INTEGER)")
    print("  - score (INTEGER)")
    print("  - highScore (INTEGER)")
    print("  - gamesPlayed (INTEGER)")
    print("  - stats (JSONB)")
    print("  - lastPlayed (TIMESTAMP)")
    print("  - updated_at (TIMESTAMP)")
