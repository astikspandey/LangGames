#!/usr/bin/env python3
"""
Test script for pastebin integration with LangGames
"""

import sys
from pastebin_client import create_pastebin_client

# Configuration
PASTEBIN_URL = "http://localhost:3001"
SITE_ID = "langgames_001"
SECRET_KEY = "5fc4cb0edec80b28daa403c85392c61340ed27d2350f0c855572fb9c30c4e9ca"

def test_connection():
    """Test pastebin connection"""
    print("Testing pastebin connection...")
    try:
        client = create_pastebin_client(PASTEBIN_URL, SITE_ID, SECRET_KEY)
        print("✓ Pastebin client created")
        return client
    except Exception as e:
        print(f"✗ Failed to create client: {e}")
        return None

def test_insert(client):
    """Test inserting data"""
    print("\nTesting data insert...")
    try:
        # Simulate game data
        test_data = {
            'user_id': 'test_user',
            'level': 5,
            'score': 1000,
            'highScore': 1500,
            'gamesPlayed': 3,
            'stats': {'accuracy': 0.85, 'speed': 120},
            'lastPlayed': '2024-11-25T12:00:00'
        }

        result = client.table('GIDbasedLV').insert(test_data).execute()
        print("✓ Data inserted successfully")
        return True
    except Exception as e:
        print(f"✗ Insert failed: {e}")
        return False

def test_select(client):
    """Test selecting data"""
    print("\nTesting data select...")
    try:
        result = client.table('GIDbasedLV').select('*').eq('user_id', 'test_user').execute()

        if result.data and len(result.data) > 0:
            print("✓ Data retrieved successfully")
            print(f"  Retrieved: {result.data[0]}")
            return result.data[0]
        else:
            print("⚠ No data found")
            return None
    except Exception as e:
        print(f"✗ Select failed: {e}")
        return None

def test_update(client, data):
    """Test updating data"""
    print("\nTesting data update...")
    try:
        # Update score
        updated_data = data.copy()
        updated_data['score'] = 2000
        updated_data['level'] = 10

        result = client.table('GIDbasedLV').update(updated_data).eq('user_id', 'test_user').execute()
        print("✓ Data updated successfully")
        return True
    except Exception as e:
        print(f"✗ Update failed: {e}")
        return False

def test_select_after_update(client):
    """Verify update worked"""
    print("\nVerifying update...")
    try:
        result = client.table('GIDbasedLV').select('*').eq('user_id', 'test_user').execute()

        if result.data and len(result.data) > 0:
            data = result.data[0]
            if data['score'] == 2000 and data['level'] == 10:
                print("✓ Update verified - data matches")
                return True
            else:
                print("⚠ Data doesn't match expected values")
                print(f"  Expected: score=2000, level=10")
                print(f"  Got: score={data['score']}, level={data['level']}")
                return False
        else:
            print("✗ No data found after update")
            return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("LangGames Pastebin Integration Test")
    print("=" * 60)

    # Test connection
    client = test_connection()
    if not client:
        print("\n✗ Cannot proceed without connection")
        sys.exit(1)

    # Test insert
    if not test_insert(client):
        print("\n⚠ Insert failed, skipping other tests")
        sys.exit(1)

    # Test select
    data = test_select(client)
    if not data:
        print("\n⚠ Select failed, skipping update test")
        sys.exit(1)

    # Test update
    if not test_update(client, data):
        print("\n⚠ Update failed")
        sys.exit(1)

    # Verify update
    if not test_select_after_update(client):
        print("\n⚠ Update verification failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nLangGames is ready to use encrypted pastebin!")
    print("Start LangGames with: python LangGames.py")

if __name__ == "__main__":
    main()
