# 🔑 API Setup Guide - Polymarket & Kalshi

Complete guide to getting API credentials for both platforms.

---

## 📋 Table of Contents
1. [Kalshi API Setup](#kalshi-api-setup)
2. [Polymarket API Setup](#polymarket-api-setup)
3. [Configuring the Bot](#configuring-the-bot)
4. [Testing Your Credentials](#testing-your-credentials)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## 🏦 Kalshi API Setup

Kalshi provides official API access with proper authentication using API keys and RSA private keys.

### Step 1: Create a Kalshi Account

1. Go to **https://kalshi.com**
2. Click **"Sign Up"**
3. Complete the registration process
4. **Verify your identity** (KYC required - US regulated platform)
   - Provide SSN or Tax ID
   - Upload government ID
   - This can take 1-3 business days

### Step 2: Fund Your Account

1. Go to **"Wallet"** → **"Deposit"**
2. Link your bank account (ACH transfer)
3. Deposit funds (minimum $10, recommended $100+ for testing)
4. **Wait 1-3 business days** for funds to clear

### Step 3: Generate API Credentials

1. Log in to Kalshi
2. Go to **Settings** (top right) → **API Keys**
3. Click **"Create New API Key"**
4. You'll see two things:
   - **API Key ID**: A string like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - **Download Private Key**: A `.pem` file

5. **Download the `.pem` file immediately!**
   - You can only download it ONCE
   - Save it securely (e.g., `~/kalshi_private_key.pem`)
   - Never share this file or commit it to git

6. Copy the **API Key ID** - you'll need this

### Step 4: Store Credentials Safely

```bash
# Move the private key to a secure location
mkdir -p ~/.kalshi
mv ~/Downloads/kalshi_private_key_*.pem ~/.kalshi/private_key.pem
chmod 600 ~/.kalshi/private_key.pem  # Restrict permissions
```

### Kalshi API Documentation

- **Official Docs**: https://trading-api.readme.io/
- **Python SDK**: https://github.com/Kalshi/kalshi-python
- **REST API**: https://trading-api.readme.io/reference/getting-started

### Kalshi API Endpoints

```
Production: https://trading-api.kalshi.com
Demo: https://demo-api.kalshi.co
```

### Example: Testing Kalshi API

```bash
# Install Kalshi Python SDK
pip install kalshi-python

# Test connection
python3 << 'EOF'
from kalshi_python.api import ApiInstance

# Replace with your credentials
api = ApiInstance(
    host="https://trading-api.kalshi.com",
    key_id="YOUR_API_KEY_ID",
    private_key_path="/path/to/kalshi_private_key.pem"
)

# Test: Get exchange status
status = api.get_exchange_status()
print(f"Kalshi API Status: {status}")

# Test: Get your balance
balance = api.get_balance()
print(f"Your Balance: ${balance['balance'] / 100:.2f}")
EOF
```

---

## 🌐 Polymarket API Setup

Polymarket is a decentralized platform on Polygon. Access requires an Ethereum wallet.

### Step 1: Create an Ethereum Wallet

You have two options:

#### Option A: MetaMask (Recommended for Beginners)

1. Install **MetaMask** browser extension
   - Chrome: https://metamask.io/download/
   - Firefox/Brave: Also available

2. Click **"Create a new wallet"**
3. Set a strong password
4. **Save your Secret Recovery Phrase** (12 words)
   - Write it down on paper
   - NEVER share it
   - Store it in a safe place

5. Complete the setup

#### Option B: Hardware Wallet (Most Secure)

- **Ledger**: https://www.ledger.com/
- **Trezor**: https://trezor.io/

### Step 2: Add Polygon Network to MetaMask

1. Open MetaMask
2. Click network dropdown (top) → **"Add Network"**
3. Select **"Polygon Mainnet"** or add manually:
   - **Network Name**: Polygon Mainnet
   - **RPC URL**: `https://polygon-rpc.com`
   - **Chain ID**: 137
   - **Currency Symbol**: MATIC
   - **Block Explorer**: `https://polygonscan.com`

### Step 3: Get USDC on Polygon

Polymarket uses **USDC on Polygon** for trading.

#### Option 1: Bridge from Ethereum

1. Buy USDC on Coinbase/Binance
2. Use Polygon Bridge: https://wallet.polygon.technology/
3. Bridge USDC from Ethereum → Polygon
4. **Costs**: Ethereum gas fees (~$5-20)

#### Option 2: Buy Directly on Polygon

1. Use a fiat on-ramp that supports Polygon:
   - **Ramp**: https://ramp.network/
   - **Transak**: https://transak.com/
   - **MoonPay**: https://www.moonpay.com/

2. Buy USDC directly on Polygon network
3. **Cheaper** than bridging

#### Option 3: Centralized Exchange (Easiest)

1. Buy USDC on **Coinbase** or **Binance**
2. Withdraw to your MetaMask address
3. **Select Polygon network** when withdrawing
4. Lowest fees (~$0.10)

### Step 4: Export Your Private Key

⚠️ **CRITICAL SECURITY WARNING**: Your private key controls all funds in your wallet!

1. Open MetaMask
2. Click **menu (3 dots)** → **Account Details**
3. Click **"Export Private Key"**
4. Enter your MetaMask password
5. **Copy the private key** (64 hex characters)
6. Store it securely (NEVER share it!)

**SECURITY TIPS**:
- Use a **dedicated wallet** for trading (not your main wallet)
- Start with **small amounts** ($50-100 for testing)
- Never paste your private key in Discord, Slack, or any chat

### Step 5: Get Polymarket API Key (Optional)

For higher rate limits, you can get an API key:

1. Go to **Polymarket Discord**: https://discord.gg/polymarket
2. Request API access in #api-access channel
3. Fill out the application form

**Note**: For basic arbitrage, the public API is sufficient.

### Polymarket API Documentation

- **CLOB API**: https://docs.polymarket.com/
- **Python Client**: https://github.com/Polymarket/py-clob-client
- **Order Book**: https://clob.polymarket.com/

### Example: Testing Polymarket API

```bash
# Install Polymarket Python client
pip install py-clob-client

# Test connection (no auth needed for public data)
python3 << 'EOF'
import requests

# Get current BTC markets
url = "https://gamma-api.polymarket.com/events?slug=bitcoin-up-or-down"
response = requests.get(url)
data = response.json()

print(f"Found {len(data)} BTC markets")
for event in data[:3]:
    print(f"  - {event['title']}")
EOF
```

---

## ⚙️ Configuring the Bot

Once you have both API credentials, configure the bot:

### Step 1: Copy Environment Template

```bash
cd polymarket-kalshi-btc-arbitrage-bot
cp .env.example .env
```

### Step 2: Edit `.env` File

```bash
nano .env  # or use any text editor
```

### Step 3: Fill in Credentials

```bash
# ============================================================================
# KALSHI CREDENTIALS
# ============================================================================
KALSHI_API_KEY=a1b2c3d4-e5f6-7890-abcd-ef1234567890
KALSHI_PRIVATE_KEY_PATH=/home/user/.kalshi/private_key.pem
KALSHI_FEE_RATE=0.07  # 7% fee

# ============================================================================
# POLYMARKET CREDENTIALS
# ============================================================================
# Your Ethereum private key (WITHOUT the 0x prefix)
POLYMARKET_PRIVATE_KEY=1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
POLYMARKET_FEE_RATE=0.0  # Near-zero with Safe Wallet

# ============================================================================
# BOT CONFIGURATION
# ============================================================================
TRADING_MODE=dry-run  # ALWAYS start with dry-run!
MIN_PROFIT=0.02
MIN_CONTRACTS=50
MAX_SLIPPAGE=0.005
SCAN_INTERVAL=2
```

### Step 4: Verify File Permissions

```bash
# Ensure .env is NOT readable by others
chmod 600 .env

# Verify it's in .gitignore
grep -q "^\.env$" .gitignore && echo "✅ .env is in .gitignore" || echo "❌ Add .env to .gitignore!"
```

---

## 🧪 Testing Your Credentials

### Test Kalshi API

```python
# test_kalshi.py
from kalshi_python.api import ApiInstance
import os

api = ApiInstance(
    host="https://trading-api.kalshi.com",
    key_id=os.getenv("KALSHI_API_KEY"),
    private_key_path=os.getenv("KALSHI_PRIVATE_KEY_PATH")
)

try:
    balance = api.get_balance()
    print(f"✅ Kalshi API connected!")
    print(f"   Balance: ${balance['balance'] / 100:.2f}")
except Exception as e:
    print(f"❌ Kalshi API failed: {e}")
```

```bash
python test_kalshi.py
```

### Test Polymarket API

```python
# test_polymarket.py
from py_clob_client.client import ClobClient
import os

client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY")
)

try:
    # Get API credentials info (this validates the key)
    print("✅ Polymarket API connected!")
    print(f"   Address: {client.get_address()}")
except Exception as e:
    print(f"❌ Polymarket API failed: {e}")
```

```bash
python test_polymarket.py
```

---

## 🔒 Security Best Practices

### ✅ DO:

1. **Use separate wallets** for different purposes:
   - Main wallet: Large holdings
   - Trading wallet: Small amounts for bot
   - Test wallet: Tiny amounts for testing

2. **Start small**:
   - Kalshi: $50-100 initially
   - Polymarket: $50-100 in USDC

3. **Use `.env` files**:
   - NEVER hardcode credentials
   - NEVER commit `.env` to git
   - Always use `.gitignore`

4. **Restrict file permissions**:
   ```bash
   chmod 600 .env
   chmod 600 ~/.kalshi/private_key.pem
   ```

5. **Enable 2FA** on Kalshi account

6. **Use hardware wallets** for large amounts

### ❌ DON'T:

1. ❌ Share your private keys with anyone
2. ❌ Paste private keys in Discord/Slack
3. ❌ Commit credentials to GitHub
4. ❌ Use your main wallet for bot trading
5. ❌ Store private keys in plain text in cloud storage
6. ❌ Use the same password for Kalshi and other services

### 🔐 Credential Storage Options

#### Option 1: Environment Variables (Development)
```bash
export KALSHI_API_KEY="your_key"
export POLYMARKET_PRIVATE_KEY="your_key"
```

#### Option 2: `.env` File (Recommended)
```bash
# .env file (in .gitignore)
KALSHI_API_KEY=your_key
POLYMARKET_PRIVATE_KEY=your_key
```

#### Option 3: AWS Secrets Manager (Production)
```bash
aws secretsmanager create-secret \
  --name arbitrage-bot/kalshi-api-key \
  --secret-string "your_key"
```

#### Option 4: Encrypted Vault (Most Secure)
- **1Password**: https://1password.com/
- **Bitwarden**: https://bitwarden.com/
- **HashiCorp Vault**: https://www.vaultproject.io/

---

## 🐛 Troubleshooting

### Kalshi Issues

#### "Invalid API Key"
```
✓ Check API Key ID is copied correctly (no spaces)
✓ Verify you're using production API (not demo)
✓ Ensure account is verified (KYC complete)
```

#### "Private Key Error"
```
✓ Check .pem file path is correct
✓ Verify file permissions: chmod 600 private_key.pem
✓ Ensure you downloaded the key (can only download once)
```

#### "Insufficient Balance"
```
✓ Check your Kalshi wallet balance
✓ Wait for ACH deposit to clear (1-3 days)
✓ Minimum $10 balance required
```

### Polymarket Issues

#### "Invalid Private Key"
```
✓ Ensure 64 hex characters (without 0x prefix)
✓ Export from MetaMask correctly
✓ Try re-exporting the key
```

#### "No USDC Balance"
```
✓ Check Polygon USDC balance (not Ethereum)
✓ Ensure you're on Polygon network
✓ Bridge or buy USDC on Polygon
```

#### "Transaction Failed"
```
✓ Check you have MATIC for gas fees (~0.1 MATIC)
✓ Verify Polygon network is working
✓ Check PolygonScan for network status
```

### General API Issues

#### Rate Limiting
```
✓ Reduce scan frequency (increase SCAN_INTERVAL)
✓ Request higher rate limits from platforms
✓ Use WebSocket instead of polling (future feature)
```

#### Network Errors
```
✓ Check internet connection
✓ Verify firewall allows HTTPS traffic
✓ Try different DNS server (8.8.8.8)
```

---

## 📞 Support Resources

### Kalshi
- **Support**: support@kalshi.com
- **Discord**: https://discord.gg/kalshi
- **API Docs**: https://trading-api.readme.io/

### Polymarket
- **Discord**: https://discord.gg/polymarket
- **Twitter**: @Polymarket
- **API Docs**: https://docs.polymarket.com/

### This Bot
- **GitHub Issues**: https://github.com/JSDIGITALLTDA/Test/issues
- **Advanced Guide**: [ADVANCED_GUIDE.md](ADVANCED_GUIDE.md)
- **Enhanced Features**: [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)

---

## 🎓 Summary Checklist

Before running the bot, ensure you have:

### Kalshi Setup
- [ ] Kalshi account created
- [ ] KYC verification complete
- [ ] Account funded ($100+)
- [ ] API Key ID obtained
- [ ] Private key `.pem` file downloaded
- [ ] Credentials tested successfully

### Polymarket Setup
- [ ] MetaMask wallet created
- [ ] Polygon network added
- [ ] USDC on Polygon obtained ($100+)
- [ ] Small amount of MATIC for gas
- [ ] Private key exported
- [ ] Credentials tested successfully

### Bot Configuration
- [ ] `.env` file created from template
- [ ] All credentials filled in
- [ ] File permissions secured (chmod 600)
- [ ] Credentials verified in .gitignore
- [ ] Test scripts run successfully

### Ready to Trade
- [ ] Ran bot in **dry-run mode** for 24+ hours
- [ ] Verified opportunity detection works
- [ ] Checked calculations are accurate
- [ ] Read all documentation
- [ ] Started with small position sizes

---

**Once you complete this checklist, you're ready to run the arbitrage bot!** 🚀

Remember: **ALWAYS start in dry-run mode** and test thoroughly before going live.
