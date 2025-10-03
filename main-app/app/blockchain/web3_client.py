import json
import os
from web3 import Web3
from typing import Tuple

class Web3Client:
    def __init__(self):
        # Connect to Hardhat local network
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        # Check connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Hardhat network")
        
        print(f"✅ Connected to blockchain")
        print(f"✅ Chain ID: {self.w3.eth.chain_id}")
        
        # Load contract info from root directory (where contract_info.json is)
        contract_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'contract_info.json')
        
        with open(contract_info_path, 'r') as f:
            contract_info = json.load(f)
        
        self.contract_address = self.w3.to_checksum_address(contract_info['address'])
        self.contract_abi = contract_info['abi']
        
        print(f"✅ Contract address: {self.contract_address}")
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        # Use first account from Hardhat
        self.account = self.w3.eth.accounts[0]
        print(f"✅ Using account: {self.account}")
        print(f"✅ Web3 client initialized successfully")

    def log_threat(self, text: str, entities: str) -> Tuple[str, int]:
        """Log threat to blockchain"""
        try:
            print(f"📝 Storing text: {text[:50]}...")
            
            # Get current threat count
            current_count = self.get_threat_count()
            print(f"📊 Current threats: {current_count}")
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account)
            
            tx = self.contract.functions.logThreat(text, entities).build_transaction({
                'from': self.account,
                'gas': 3000000,
                'gasPrice': self.w3.to_wei('1', 'gwei'),
                'nonce': nonce,
                'chainId': 1337
            })
            
            # Sign transaction
            private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
            
            # Send transaction
            if hasattr(signed_tx, 'rawTransaction'):
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"✅ Confirmed in block {receipt['blockNumber']}")
            
            return self.w3.to_hex(tx_hash), current_count
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise Exception(f"Failed to log threat: {str(e)}")

    def get_threat_count(self) -> int:
        """Get total number of threats"""
        return self.contract.functions.getThreatCount().call()

    def get_threat(self, threat_id: int) -> dict:
        """Get threat details by ID"""
        try:
            # Use the public getter function for threats array
            threat = self.contract.functions.threats(threat_id).call()
            
            return {
                "text": threat[0],
                "entities": threat[1], 
                "timestamp": threat[2],
                "submitter": threat[3]
            }
        except Exception as e:
            print(f"Error getting threat {threat_id}: {e}")
            raise Exception(f"Threat not found: {str(e)}")
