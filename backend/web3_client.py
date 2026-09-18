import logging
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted
from config import settings

logger = logging.getLogger("AegisChain-Web3")

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))

if not w3.is_connected():
    logger.error(f"CRITICAL: Failed to connect to Web3 Provider at {settings.WEB3_PROVIDER_URL}")
else:
    logger.info(f"Successfully connected to Web3 Provider. Chain ID: {w3.eth.chain_id}")

# Minimal ABI matching the SupplyChain.sol contract from Part 1
SUPPLY_CHAIN_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_batchId", "type": "string"},
            {"internalType": "string", "name": "_medicineName", "type": "string"},
            {"internalType": "string", "name": "_dataHash", "type": "string"}
        ],
        "name": "registerBatch",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_batchId", "type": "string"},
            {"internalType": "string", "name": "_location", "type": "string"},
            {"internalType": "string", "name": "_temperatureData", "type": "string"}
        ],
        "name": "updateTransit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_batchId", "type": "string"}],
        "name": "getTransitHistory",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "handler", "type": "address"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "location", "type": "string"},
                    {"internalType": "string", "name": "temperatureData", "type": "string"}
                ],
                "internalType": "struct SupplyChain.TransitRecord[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Instantiate contract
contract = w3.eth.contract(address=w3.to_checksum_address(settings.CONTRACT_ADDRESS), abi=SUPPLY_CHAIN_ABI)
account = w3.eth.account.from_key(settings.PRIVATE_KEY)

def _build_and_send_tx(func_call):
    """
    Helper function to estimate gas, build, sign, and broadcast a transaction securely.
    """
    nonce = w3.eth.get_transaction_count(account.address)
    
    try:
        # Build transaction parameters
        tx = func_call.build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 2000000, # Fallback, will be overridden by estimate
            'maxFeePerGas': w3.to_wei('2', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
            'nonce': nonce,
        })
        
        # Optimize gas estimation
        tx['gas'] = w3.eth.estimate_gas(tx)
        
        # Sign the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=settings.PRIVATE_KEY)
        
        # Broadcast to network
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt to ensure it is mined (crucial for live hackathon demos)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status != 1:
            raise Exception("Transaction failed on-chain (reverted).")
            
        return tx_hash.hex()

    except ContractLogicError as cle:
        logger.error(f"Contract logic error: {cle}")
        raise ValueError(f"Smart Contract execution failed: {cle}")
    except TimeExhausted:
        logger.error("Transaction confirmation timeout.")
        raise Exception("Network congested. Transaction broadcasted but not yet mined.")
    except Exception as e:
        logger.error(f"Transaction broadcasting failed: {e}")
        raise

async def register_batch_on_chain(batch_id: str, medicine_name: str, data_hash: str) -> str:
    """Invokes the registerBatch smart contract function."""
    logger.info(f"Initiating Web3 Tx: Registering Batch {batch_id}")
    func_call = contract.functions.registerBatch(batch_id, medicine_name, data_hash)
    return _build_and_send_tx(func_call)

async def update_transit_on_chain(batch_id: str, location: str, temperature_data: str) -> str:
    """Invokes the updateTransit smart contract function."""
    logger.info(f"Initiating Web3 Tx: Updating Transit for Batch {batch_id}")
    func_call = contract.functions.updateTransit(batch_id, location, temperature_data)
    return _build_and_send_tx(func_call)

async def get_batch_history(batch_id: str) -> list:
    """
    Reads the immutable transit history from the blockchain.
    This is a 'view' function and does not cost gas.
    """
    logger.info(f"Querying Web3 Ledger: Fetching history for {batch_id}")
    try:
        raw_history = contract.functions.getTransitHistory(batch_id).call()
        
        # Format the raw tuple data into readable dictionaries
        formatted_history = []
        for record in raw_history:
            formatted_history.append({
                "handler_address": record[0],
                "timestamp": record[1], # Will be converted to datetime in main.py if needed
                "location": record[2],
                "temperature_data": record[3]
            })
        return formatted_history
        
    except ContractLogicError as cle:
        logger.error(f"Failed to fetch history for {batch_id}: {cle}")
        raise ValueError("Batch not found or not registered on-chain.")