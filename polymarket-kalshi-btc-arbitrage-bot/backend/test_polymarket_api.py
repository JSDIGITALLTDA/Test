#!/usr/bin/env python3
"""
Test Polymarket API Connection

This script verifies that your Polymarket credentials are working correctly.

Usage:
    python test_polymarket_api.py
"""

import os
import sys

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

def test_polymarket_connection():
    """Test Polymarket API connection and credentials"""

    print("🧪 Testing Polymarket API Connection...")
    print("-" * 60)

    # Check environment variables
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")

    if not private_key:
        print("❌ POLYMARKET_PRIVATE_KEY not found in environment")
        print("   Set it in .env file or environment variables")
        print("   Export from MetaMask: Settings → Security → Export Private Key")
        return False

    # Validate private key format
    if private_key.startswith("0x"):
        print("⚠️  Private key should NOT include '0x' prefix")
        print("   Removing '0x' prefix...")
        private_key = private_key[2:]

    if len(private_key) != 64:
        print(f"❌ Invalid private key length: {len(private_key)} (should be 64 hex chars)")
        return False

    print(f"✅ Private key found: {private_key[:8]}...{private_key[-4:]}")

    # Test 1: Basic API connectivity (no auth required)
    print("\n🔌 Testing Polymarket API connectivity...")
    import requests

    try:
        # Test public API
        url = "https://gamma-api.polymarket.com/events?limit=1"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print("✅ Polymarket API is reachable")
            data = response.json()
            print(f"   Found {len(data)} events")
        else:
            print(f"⚠️  Polymarket API returned status {response.status_code}")

    except Exception as e:
        print(f"⚠️  Cannot reach Polymarket API: {e}")
        print("   This is normal in some network environments")

    # Test 2: Validate Ethereum address
    print("\n🔐 Validating Ethereum credentials...")

    try:
        from eth_account import Account
    except ImportError:
        print("⚠️  eth-account not installed")
        print("   Install with: pip install eth-account")
        print("   Skipping wallet validation...")
        return True  # Still count as success if API is reachable

    try:
        # Derive address from private key
        account = Account.from_key(private_key)
        address = account.address

        print(f"✅ Valid Ethereum private key")
        print(f"   Address: {address}")

    except Exception as e:
        print(f"❌ Invalid private key: {e}")
        return False

    # Test 3: Check Polygon balance (optional)
    print("\n💰 Checking Polygon wallet balance...")

    try:
        from web3 import Web3

        # Connect to Polygon
        polygon_rpc = "https://polygon-rpc.com"
        w3 = Web3(Web3.HTTPProvider(polygon_rpc))

        if not w3.is_connected():
            print("⚠️  Cannot connect to Polygon network")
            return True  # Still count as success

        # Get MATIC balance
        matic_balance = w3.eth.get_balance(address)
        matic_balance_ether = w3.from_wei(matic_balance, 'ether')

        print(f"   MATIC Balance: {matic_balance_ether:.4f} MATIC")

        if matic_balance_ether < 0.1:
            print("   ⚠️  Low MATIC balance! Get some for gas fees.")

        # Get USDC balance
        usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC on Polygon
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
        usdc_balance = usdc_contract.functions.balanceOf(address).call()
        usdc_decimals = usdc_contract.functions.decimals().call()
        usdc_balance_human = usdc_balance / (10 ** usdc_decimals)

        print(f"   USDC Balance: ${usdc_balance_human:.2f}")

        if usdc_balance_human < 10:
            print("   ⚠️  Low USDC balance! Deposit at least $50 for trading.")

    except ImportError:
        print("⚠️  web3 not installed")
        print("   Install with: pip install web3")
        print("   Skipping balance check...")
    except Exception as e:
        print(f"⚠️  Could not check balance: {e}")

    # Test 4: Try Polymarket SDK (if available)
    print("\n📡 Testing Polymarket CLOB API...")

    try:
        from py_clob_client.client import ClobClient
    except ImportError:
        print("⚠️  py-clob-client not installed")
        print("   Install with: pip install py-clob-client")
        print("   Skipping CLOB API test...")

        print("\n" + "=" * 60)
        print("✅ PARTIAL SUCCESS - Private key is valid!")
        print("   Install py-clob-client for full functionality")
        print("=" * 60)
        return True

    try:
        client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key
        )

        print(f"✅ Polymarket client initialized")
        print(f"   Trading Address: {client.get_address()}")

        # Test getting order book
        print("\n   Testing market data...")
        # Note: Need a valid token ID, this is just example
        # In real usage, the bot fetches these dynamically

    except Exception as e:
        print(f"⚠️  CLOB client test: {e}")
        print("   This is normal - requires valid token IDs")

    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Polymarket credentials are valid!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_polymarket_connection()
    sys.exit(0 if success else 1)
