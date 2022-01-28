from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv
install_solc("0.6.0")
load_dotenv()


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)


compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# print(compiled_sol)

with open("compiled_code.json", "w") as file:
    # compiled json varaible
    json.dump(compiled_sol, file)

# get byte code
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

print(abi)

# local ganache chain
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/92164ab9ce034b5aa1a048cfe180663b"))
# network id = 5777, chain id = 1337
chain_id = 4

my_address = "0x1307DD272982cC601b4ef2f60b60f237CdD46D4D"
private_key = os.getenv("PRIVATE_KEY")
# print(private_key)


# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
print(nonce)

# 1. build a transaction
# 2. sign a transaction
# 3. send a transaction
transaction = SimpleStorage.constructor().buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId":chain_id,
    "from": my_address,
    "nonce": nonce
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

print("Deploying contract ...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Deployed")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# working with the contract
# contract Address
# contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
# print(simple_storage.functions.store(15).call())
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    { "chainId": chain_id, "from": my_address, "gasPrice": w3.eth.gas_price, "nonce": nonce +1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

print("Updating contract ...")
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updated")

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
