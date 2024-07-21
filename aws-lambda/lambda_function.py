import json
import base64
import os
from solana.rpc.api import Client
from solana.transaction import Transaction, AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.account import Account

def lambda_handler(event, context):
    # Parse the incoming data
    data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    temperature = data['temperature']
    humidity = data['humidity']

    # Solana setup
    client = Client("https://api.devnet.solana.com")

    # Retrieve private key from environment variable
    private_key = json.loads(base64.b64decode("pUOzvGWuXhhkQp1ck3214rJC/9d/vx5f9+7LSxbl14I="))
    payer = Account(private_key)

    # Replace with your actual program ID (Public Key)
    program_id = Pubkey("815ZrwvtXyVMWeVfunYVDXSvBQ13nNrKr671PbtNGZvm")

    # Create the instruction data
    instruction_data = temperature.to_bytes(4, 'little') + humidity.to_bytes(4, 'little')

    # Create the transaction instruction
    transaction_instruction = Instruction(
        keys=[
            AccountMeta(pubkey=payer.public_key(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        ],
        program_id=program_id,
        data=instruction_data
    )

    # Create the transaction
    transaction = Transaction().add(transaction_instruction)

    # Send the transaction
    response = client.send_transaction(transaction, payer)
    print(response)

    return {
        'statusCode': 200,
        'body': json.dumps('Data published to Solana')
    }