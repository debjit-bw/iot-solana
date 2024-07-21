import os
import json
import base64

with open('/Users/debjit/solana-wallet.json', 'r') as f:
    keypair = json.load(f)

# The private key is the first 32 bytes of the keypair
private_key = keypair[0:32]
print(private_key)

# The private key is the first 32 bytes of the keypair
private_key = keypair[:32]

# Base64 encode the private key
encoded_private_key = base64.b64encode(bytes(private_key)).decode('utf-8')

# Set the environment variable
os.environ['SOLANA_PRIVATE_KEY'] = encoded_private_key

# Print to verify (for debugging purposes, you might want to remove this in production)
print(f"Encoded private key set as environment variable: {encoded_private_key}")