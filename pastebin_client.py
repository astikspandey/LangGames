"""
Pastebin Client for LangGames
Replaces Supabase with encrypted pastebin backend
"""

import requests
import hashlib
import time
import json
import logging
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Configure logging
logger = logging.getLogger(__name__)


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

    def _encrypt_payload(self, data):
        """Encrypt entire request payload with secret key only"""
        key_hash = hashlib.sha256(self.secret_key.encode()).digest()
        iv = get_random_bytes(16)

        cipher = AES.new(key_hash, AES.MODE_CBC, iv)

        # Pad data to 16-byte boundary
        data_str = json.dumps(data)
        padding_length = 16 - (len(data_str) % 16)
        padded_data = data_str + (chr(padding_length) * padding_length)

        encrypted = cipher.encrypt(padded_data.encode('utf-8'))

        return {
            'encrypted_payload': encrypted.hex(),
            'payload_iv': iv.hex()
        }

    def _decrypt_payload(self, encrypted_hex, iv_hex):
        """Decrypt entire response payload with secret key only"""
        key_hash = hashlib.sha256(self.secret_key.encode()).digest()
        iv = bytes.fromhex(iv_hex)

        cipher = AES.new(key_hash, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(bytes.fromhex(encrypted_hex))

        # Remove padding
        padding_length = decrypted[-1]
        decrypted = decrypted[:-padding_length]

        return json.loads(decrypted.decode('utf-8'))

    def handshake(self):
        """Perform handshake with pastebin"""
        try:
            logger.debug(f"🤝 Starting handshake with {self.pastebin_url}")

            # Step 1: Initiate handshake
            response = requests.get(f"{self.pastebin_url}/handshake", params={
                'site_id': self.site_id
            })
            response.raise_for_status()
            result = response.json()

            session_id = result['session_id']
            challenge = result['challenge']
            logger.debug(f"🔑 Received challenge from pastebin")

            # Step 2: Verify we have correct secret key
            our_hash = self._sha256(self.secret_key)
            if our_hash != challenge:
                logger.error(f"❌ Secret key mismatch! Expected: {challenge[:10]}..., Got: {our_hash[:10]}...")
                raise Exception('Secret key mismatch')

            # Step 3: Send verification
            verify_response = requests.post(f"{self.pastebin_url}/verify", json={
                'session_id': session_id,
                'proof': our_hash
            })
            verify_response.raise_for_status()

            logger.info(f"✅ Handshake successful with {self.pastebin_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Handshake failed: {type(e).__name__}: {str(e)}")
            raise

    def store(self, location, data, metadata=None):
        """Store data in pastebin with optional metadata"""
        try:
            logger.info(f"💾 Storing data to pastebin (location={location})")
            if metadata:
                logger.debug(f"📋 Metadata: {metadata}")

            # Perform handshake
            self.handshake()

            # Get current epoch
            epoch = int(time.time())

            # Encrypt the data
            encrypted_result = self._encrypt(data, epoch)
            logger.debug(f"🔐 Data encrypted (size={len(encrypted_result['encrypted'])} bytes)")

            # Generate auth proof
            auth_proof = self._generate_auth_proof(epoch)

            # Prepare request payload
            payload = {
                'time': epoch,
                'encrypted_info': encrypted_result['encrypted'],
                'loc': location,
                'iv': encrypted_result['iv'],
                'enc': auth_proof
            }

            # Add metadata fields if provided
            if metadata:
                payload.update(metadata)

            # Encrypt the entire payload
            encrypted_payload = self._encrypt_payload(payload)

            # Send to pastebin (only site_id is unencrypted)
            logger.debug(f"📤 Sending to {self.pastebin_url}/store")
            response = requests.post(f"{self.pastebin_url}/store", json={
                'site_id': self.site_id,
                **encrypted_payload
            })
            response.raise_for_status()

            # Decrypt response
            result = response.json()
            if 'encrypted_payload' in result:
                result = self._decrypt_payload(result['encrypted_payload'], result['payload_iv'])

            logger.info(f"✅ Data stored successfully (id={result.get('id', 'unknown')})")
            return result
        except Exception as e:
            logger.error(f"❌ Store failed: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def retrieve(self, location=None):
        """Retrieve data from pastebin"""
        try:
            logger.info(f"📥 Retrieving data from pastebin (location={location or 'all'})")
            epoch = int(time.time())
            auth_proof = self._generate_auth_proof(epoch)

            # Prepare request payload
            payload = {
                'enc': auth_proof,
                'epo': epoch
            }

            if location:
                payload['loc'] = location

            # Encrypt the payload
            encrypted_payload = self._encrypt_payload(payload)

            # Send to pastebin (only site_id is unencrypted)
            logger.debug(f"📤 Sending to {self.pastebin_url}/retrieve")
            response = requests.post(f"{self.pastebin_url}/retrieve", json={
                'site_id': self.site_id,
                **encrypted_payload
            })
            response.raise_for_status()

            # Decrypt response
            result = response.json()
            if 'encrypted_payload' in result:
                result = self._decrypt_payload(result['encrypted_payload'], result['payload_iv'])

            logger.debug(f"📦 Received {len(result.get('data', []))} items from pastebin")

            # Decrypt the retrieved data
            decrypted_data = []
            for item in result.get('data', []):
                try:
                    decrypted = self._decrypt(
                        item['encrypted_data'],
                        item['iv'],
                        item['epoch']
                    )
                    paste_item = {
                        'id': item['id'],
                        'location': item['location'],
                        'data': decrypted,
                        'epoch': item['epoch'],
                        'created_at': item['created_at']
                    }

                    # Include metadata if present
                    if 'metadata' in item:
                        paste_item['metadata'] = item['metadata']
                        logger.debug(f"📋 Metadata blob: {item['metadata'][:50]}...")
                    if 'metadata_parsed' in item:
                        paste_item['metadata_parsed'] = item['metadata_parsed']

                    decrypted_data.append(paste_item)
                except Exception as e:
                    logger.error(f"❌ Failed to decrypt item {item['id']}: {e}")

            logger.info(f"✅ Successfully retrieved {len(decrypted_data)} items")
            return decrypted_data
        except Exception as e:
            logger.error(f"❌ Retrieve failed: {type(e).__name__}: {str(e)}")
            raise

    def update(self, paste_id, data, metadata=None):
        """Update existing data with optional metadata"""
        try:
            logger.info(f"🔄 Updating paste {paste_id}")
            if metadata:
                logger.debug(f"📋 Metadata: {metadata}")

            self.handshake()

            epoch = int(time.time())
            encrypted_result = self._encrypt(data, epoch)
            auth_proof = self._generate_auth_proof(epoch)

            # Prepare request payload
            payload = {
                'paste_id': paste_id,
                'time': epoch,
                'encrypted_info': encrypted_result['encrypted'],
                'iv': encrypted_result['iv'],
                'enc': auth_proof
            }

            # Add metadata fields if provided
            if metadata:
                payload.update(metadata)

            # Encrypt the payload
            encrypted_payload = self._encrypt_payload(payload)

            logger.debug(f"📤 Sending to {self.pastebin_url}/update")
            response = requests.put(f"{self.pastebin_url}/update", json={
                'site_id': self.site_id,
                **encrypted_payload
            })
            response.raise_for_status()

            # Decrypt response
            result = response.json()
            if 'encrypted_payload' in result:
                result = self._decrypt_payload(result['encrypted_payload'], result['payload_iv'])

            logger.info(f"✅ Paste {paste_id} updated successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Update failed: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def delete(self, paste_id):
        """Delete data"""
        try:
            logger.info(f"🗑️  Deleting paste {paste_id}")
            epoch = int(time.time())
            auth_proof = self._generate_auth_proof(epoch)

            # Prepare request payload
            payload = {
                'paste_id': paste_id,
                'enc': auth_proof,
                'epo': epoch
            }

            # Encrypt the payload
            encrypted_payload = self._encrypt_payload(payload)

            response = requests.delete(f"{self.pastebin_url}/delete", json={
                'site_id': self.site_id,
                **encrypted_payload
            })
            response.raise_for_status()

            # Decrypt response
            result = response.json()
            if 'encrypted_payload' in result:
                result = self._decrypt_payload(result['encrypted_payload'], result['payload_iv'])

            logger.info(f"✅ Paste {paste_id} deleted successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Delete failed: {type(e).__name__}: {str(e)}")
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
        # Clear update state to avoid conflicts
        if hasattr(self, '_update_data'):
            delattr(self, '_update_data')
        if hasattr(self, '_update_filter'):
            delattr(self, '_update_filter')
        return self

    def eq(self, column, value):
        """Filter by equality (mimics Supabase interface)"""
        # Check if this is an update operation
        if hasattr(self, '_update_data') and self._update_data is not None:
            # This is an update operation - store filter but don't execute yet
            self._update_filter = (column, value)
            return self
        else:
            # This is a select operation
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
        # Check if this is an update operation
        if hasattr(self, '_update_data') and self._update_data is not None:
            return self.execute_update()

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
                result = type('obj', (object,), {'data': [data]})
            else:
                result = type('obj', (object,), {'data': []})

            # Clear state after execution to prevent conflicts with next operation
            self._filters = {}
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')

            return result
        except Exception as e:
            logger.error(f"❌ Query error: {type(e).__name__}: {str(e)}", exc_info=True)
            # Clear state even on error
            self._filters = {}
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')
            return type('obj', (object,), {'data': []})

    def insert(self, data):
        """Insert data (mimics Supabase interface)"""
        user_id = data.get('user_id', 'default_user')

        try:
            # Extract metadata fields (fields that should be searchable/filterable)
            metadata = {}
            metadata_fields = ['level', 'score', 'highScore', 'gamesPlayed', 'lastPlayed']

            for field in metadata_fields:
                if field in data:
                    metadata[field] = data[field]

            result = self.client.store(location=user_id, data=data, metadata=metadata)

            # Clear state after insert
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')

            return type('obj', (object,), {'data': [data]})
        except Exception as e:
            logger.error(f"❌ Insert error: {type(e).__name__}: {str(e)}", exc_info=True)
            # Clear state even on error
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')
            raise

    def update(self, data):
        """Update data (mimics Supabase interface)"""
        self._update_data = data
        self._update_filter = None
        return self

    def execute_update(self):
        """Execute the update operation"""
        column, user_id = self._update_filter

        try:
            # Extract metadata fields
            metadata = {}
            metadata_fields = ['level', 'score', 'highScore', 'gamesPlayed', 'lastPlayed']

            for field in metadata_fields:
                if field in self._update_data:
                    metadata[field] = self._update_data[field]

            # Get existing paste_id
            results = self.client.retrieve(location=user_id)
            if results:
                paste_id = results[0]['id']
                result = self.client.update(paste_id, self._update_data, metadata=metadata)
                update_result = type('obj', (object,), {'data': [self._update_data]})
            else:
                # No existing data, insert instead
                self._update_data['user_id'] = user_id
                update_result = self.insert(self._update_data)

            # Clear state after update
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')

            return update_result
        except Exception as e:
            logger.error(f"❌ Update error: {type(e).__name__}: {str(e)}", exc_info=True)
            # Clear state even on error
            if hasattr(self, '_update_data'):
                delattr(self, '_update_data')
            if hasattr(self, '_update_filter'):
                delattr(self, '_update_filter')
            raise


def create_pastebin_client(pastebin_url, site_id, secret_key):
    """Create a Supabase-like client that uses encrypted pastebin"""
    client = PastebinClient(pastebin_url, site_id, secret_key)
    return PastebinAdapter(client)
