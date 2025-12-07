"""
Pastebin Client for LangGames
Replaces Supabase with encrypted pastebin backend
"""

import requests
import hashlib
import time
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class PastebinClient:
    """Client for encrypted pastebin service"""

    def __init__(self, pastebin_url, site_id, secret_key):
        self.pastebin_url = pastebin_url
        self.site_id = site_id
        self.secret_key = secret_key

    def _sha256(self, data):
        """Generate SHA256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _encrypt(self, data, epoch):
        """Encrypt data using AES-256-CBC"""
        combined_key = self.secret_key + str(epoch)
        key_hash = hashlib.sha256(combined_key.encode()).digest()
        iv = get_random_bytes(16)

        cipher = AES.new(key_hash, AES.MODE_CBC, iv)

        # Pad data to 16-byte boundary
        data_str = json.dumps(data)
        padding_length = 16 - (len(data_str) % 16)
        padded_data = data_str + (chr(padding_length) * padding_length)

        encrypted = cipher.encrypt(padded_data.encode('utf-8'))

        return {
            'encrypted': encrypted.hex(),
            'iv': iv.hex()
        }

    def _decrypt(self, encrypted_hex, iv_hex, epoch):
        """Decrypt data using AES-256-CBC"""
        combined_key = self.secret_key + str(epoch)
        key_hash = hashlib.sha256(combined_key.encode()).digest()
        iv = bytes.fromhex(iv_hex)

        cipher = AES.new(key_hash, AES.MODE_CBC, iv)
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = cipher.decrypt(encrypted).decode('utf-8')

        # Remove padding
        padding_length = ord(decrypted[-1])
        decrypted = decrypted[:-padding_length]

        return json.loads(decrypted)

    def _generate_auth_proof(self, epoch):
        """Generate authentication proof"""
        return self._sha256(self.secret_key + str(epoch))

    def handshake(self):
        """Perform handshake with pastebin"""
        try:
            # Step 1: Initiate handshake
            response = requests.get(f"{self.pastebin_url}/handshake", params={
                'site_id': self.site_id
            })
            response.raise_for_status()
            result = response.json()

            session_id = result['session_id']
            challenge = result['challenge']

            # Step 2: Verify we have correct secret key
            our_hash = self._sha256(self.secret_key)
            if our_hash != challenge:
                raise Exception('Secret key mismatch')

            # Step 3: Send verification
            verify_response = requests.post(f"{self.pastebin_url}/verify", json={
                'session_id': session_id,
                'proof': our_hash
            })
            verify_response.raise_for_status()

            return True
        except Exception as e:
            print(f"Handshake failed: {e}")
            raise

    def store(self, location, data):
        """Store data in pastebin"""
        try:
            # Perform handshake
            self.handshake()

            # Get current epoch
            epoch = int(time.time())

            # Encrypt the data
            encrypted_result = self._encrypt(data, epoch)

            # Generate auth proof
            auth_proof = self._generate_auth_proof(epoch)

            # Send to pastebin
            response = requests.post(f"{self.pastebin_url}/store", json={
                'site_id': self.site_id,
                'time': epoch,
                'encrypted_info': encrypted_result['encrypted'],
                'loc': location,
                'iv': encrypted_result['iv'],
                'enc': auth_proof
            })
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Store failed: {e}")
            raise

    def retrieve(self, location=None):
        """Retrieve data from pastebin"""
        try:
            epoch = int(time.time())
            auth_proof = self._generate_auth_proof(epoch)

            params = {
                'site_id': self.site_id,
                'enc': auth_proof,
                'epo': epoch
            }

            if location:
                params['loc'] = location

            response = requests.get(f"{self.pastebin_url}/retrieve", params=params)
            response.raise_for_status()
            result = response.json()

            # Decrypt the retrieved data
            decrypted_data = []
            for item in result.get('data', []):
                try:
                    decrypted = self._decrypt(
                        item['encrypted_data'],
                        item['iv'],
                        item['epoch']
                    )
                    decrypted_data.append({
                        'id': item['id'],
                        'location': item['location'],
                        'data': decrypted,
                        'epoch': item['epoch'],
                        'created_at': item['created_at']
                    })
                except Exception as e:
                    print(f"Failed to decrypt item {item['id']}: {e}")

            return decrypted_data
        except Exception as e:
            print(f"Retrieve failed: {e}")
            raise

    def update(self, paste_id, data):
        """Update existing data"""
        try:
            self.handshake()

            epoch = int(time.time())
            encrypted_result = self._encrypt(data, epoch)
            auth_proof = self._generate_auth_proof(epoch)

            response = requests.put(f"{self.pastebin_url}/update", json={
                'site_id': self.site_id,
                'paste_id': paste_id,
                'time': epoch,
                'encrypted_info': encrypted_result['encrypted'],
                'iv': encrypted_result['iv'],
                'enc': auth_proof
            })
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Update failed: {e}")
            raise

    def delete(self, paste_id):
        """Delete data"""
        try:
            epoch = int(time.time())
            auth_proof = self._generate_auth_proof(epoch)

            response = requests.delete(f"{self.pastebin_url}/delete", json={
                'site_id': self.site_id,
                'paste_id': paste_id,
                'enc': auth_proof,
                'epo': epoch
            })
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Delete failed: {e}")
            raise


class PastebinAdapter:
    """
    Adapter to make PastebinClient work like Supabase client
    Provides a Supabase-like interface for LangGames
    """

    def __init__(self, pastebin_client):
        self.client = pastebin_client
        self._table_name = None

    def table(self, table_name):
        """Select table (mimics Supabase interface)"""
        self._table_name = table_name
        return self

    def select(self, columns='*'):
        """Select columns (mimics Supabase interface)"""
        self._columns = columns
        self._filters = {}
        self._order_by = None
        self._limit_count = None
        return self

    def eq(self, column, value):
        """Filter by equality (mimics Supabase interface)"""
        self._filters[column] = value
        return self

    def order(self, column, desc=False):
        """Order results (mimics Supabase interface)"""
        self._order_by = (column, desc)
        return self

    def limit(self, count):
        """Limit results (mimics Supabase interface)"""
        self._limit_count = count
        return self

    def execute(self):
        """Execute the query"""
        # For GIDbasedLV table, user_id is the location
        user_id = self._filters.get('user_id', 'default_user')

        try:
            # Retrieve data for this user
            results = self.client.retrieve(location=user_id)

            if results:
                # Return the most recent one (already sorted by created_at desc in pastebin)
                data = results[0]['data']
                # Add paste_id for update operations
                data['_paste_id'] = results[0]['id']
                return type('obj', (object,), {'data': [data]})
            else:
                return type('obj', (object,), {'data': []})
        except Exception as e:
            print(f"Query error: {e}")
            return type('obj', (object,), {'data': []})

    def insert(self, data):
        """Insert data (mimics Supabase interface)"""
        user_id = data.get('user_id', 'default_user')

        try:
            result = self.client.store(location=user_id, data=data)
            return type('obj', (object,), {'data': [data]})
        except Exception as e:
            print(f"Insert error: {e}")
            raise

    def update(self, data):
        """Update data (mimics Supabase interface)"""
        self._update_data = data
        self._update_filter = None
        return self

    def eq(self, column, value):
        """Filter for various operations"""
        if hasattr(self, '_update_data'):
            # This is an update operation
            self._update_filter = (column, value)
            return self.execute_update()
        else:
            # This is a select operation
            self._filters[column] = value
            return self

    def execute_update(self):
        """Execute the update operation"""
        column, user_id = self._update_filter

        try:
            # Get existing paste_id
            results = self.client.retrieve(location=user_id)
            if results:
                paste_id = results[0]['id']
                result = self.client.update(paste_id, self._update_data)
                return type('obj', (object,), {'data': [self._update_data]})
            else:
                # No existing data, insert instead
                self._update_data['user_id'] = user_id
                return self.insert(self._update_data)
        except Exception as e:
            print(f"Update error: {e}")
            raise


def create_pastebin_client(pastebin_url, site_id, secret_key):
    """Create a Supabase-like client that uses encrypted pastebin"""
    client = PastebinClient(pastebin_url, site_id, secret_key)
    return PastebinAdapter(client)
