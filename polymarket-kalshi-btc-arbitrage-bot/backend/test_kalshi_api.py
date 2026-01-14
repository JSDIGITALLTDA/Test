#!/usr/bin/env python3
"""
Test Kalshi API Connection

This script verifies that your Kalshi API credentials are working correctly.

Usage:
    python test_kalshi_api.py
"""

import os
import sys
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

def test_kalshi_connection():
    """Test Kalshi API connection and credentials"""

    print("🧪 Testing Kalshi API Connection...")
    print("-" * 60)

    # Check environment variables
    api_key = os.getenv("KALSHI_API_KEY")
    private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")

    if not api_key:
        print("❌ KALSHI_API_KEY not found in environment")
        print("   Set it in .env file or environment variables")
        return False

    if not private_key_path:
        print("❌ KALSHI_PRIVATE_KEY_PATH not found in environment")
        print("   Set it in .env file or environment variables")
        return False

    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    print(f"✅ Private key path: {private_key_path}")

    # Check if private key file exists
    if not Path(private_key_path).exists():
        print(f"❌ Private key file not found at: {private_key_path}")
        print("   Download it from Kalshi Settings → API Keys")
        return False

    print(f"✅ Private key file exists")

    # Try to import Kalshi SDK
    try:
        from kalshi_python.api import ApiInstance
    except ImportError:
        print("⚠️  kalshi-python SDK not installed")
        print("   Install with: pip install kalshi-python")
        print("\n   For now, testing basic connectivity...")

        # Test with requests
        import requests
        try:
            response = requests.get("https://trading-api.kalshi.com/trade-api/v2/exchange/status", timeout=5)
            if response.status_code == 200:
                print("✅ Kalshi API is reachable")
                print(f"   Exchange Status: {response.json()}")
                return True
            else:
                print(f"❌ Kalshi API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach Kalshi API: {e}")
            return False

    # Test with SDK
    try:
        print("\n🔌 Connecting to Kalshi API...")
        api = ApiInstance(
            host="https://trading-api.kalshi.com",
            key_id=api_key,
            private_key_path=private_key_path
        )

        # Test 1: Get exchange status
        print("   Testing exchange status...")
        status = api.get_exchange_status()
        print(f"   ✅ Exchange Status: {status}")

        # Test 2: Get balance
        print("\n   Testing account balance...")
        balance = api.get_balance()
        balance_dollars = balance['balance'] / 100  # Convert cents to dollars
        print(f"   ✅ Account Balance: ${balance_dollars:.2f}")

        if balance_dollars < 10:
            print("   ⚠️  Low balance! Deposit at least $50 for trading.")

        # Test 3: Get markets
        print("\n   Testing market data...")
        markets = api.get_markets(limit=3)
        print(f"   ✅ Found {len(markets['markets'])} markets")
        for market in markets['markets'][:3]:
            print(f"      - {market['ticker']}: {market['title']}")

        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Kalshi API is working correctly!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Kalshi API test failed: {e}")
        print("\nPossible issues:")
        print("  1. API Key ID is incorrect")
        print("  2. Private key file is wrong or corrupted")
        print("  3. Account is not verified (KYC incomplete)")
        print("  4. Network connectivity issues")
        return False


if __name__ == "__main__":
    success = test_kalshi_connection()
    sys.exit(0 if success else 1)
