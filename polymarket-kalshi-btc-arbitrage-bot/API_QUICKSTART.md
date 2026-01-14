# ⚡ API Quick Start - 5 Minute Setup

**TL;DR**: Get your bot running in 5 minutes.

---

## 🏦 Kalshi (3 minutes)

### 1. Create Account
- Go to **https://kalshi.com/signup**
- Complete KYC (1-3 business days wait)

### 2. Get API Credentials
```
Settings → API Keys → Create New API Key
```

You'll get:
- **API Key ID**: Copy this string
- **Private Key**: Download `.pem` file

### 3. Save Credentials
```bash
mkdir -p ~/.kalshi
mv ~/Downloads/kalshi_*.pem ~/.kalshi/private_key.pem
chmod 600 ~/.kalshi/private_key.pem
```

### 4. Fund Account
```
Wallet → Deposit → Link Bank → Transfer $100
```

---

## 🌐 Polymarket (2 minutes)

### 1. Install MetaMask
- Chrome: **https://metamask.io**
- Create new wallet, save 12-word phrase

### 2. Add Polygon Network
```
MetaMask → Networks → Add Network → Polygon Mainnet
```

Or manually:
- **RPC**: `https://polygon-rpc.com`
- **Chain ID**: `137`

### 3. Get USDC on Polygon

**Easiest**: Buy on Coinbase, withdraw to Polygon
```
Coinbase → USDC → Send → [Your Address] → Polygon Network
```

**Cheapest**: Use Ramp.network
```
https://ramp.network/ → Buy USDC → Polygon → $100
```

### 4. Export Private Key
```
MetaMask → ⋮ Menu → Account Details → Export Private Key
```

⚠️ **NEVER share this key!**

---

## ⚙️ Configure Bot

### 1. Create `.env` File
```bash
cd polymarket-kalshi-btc-arbitrage-bot
cp .env.example .env
nano .env
```

### 2. Fill in Credentials
```bash
# Kalshi
KALSHI_API_KEY=your_api_key_id_here
KALSHI_PRIVATE_KEY_PATH=/home/user/.kalshi/private_key.pem

# Polymarket
POLYMARKET_PRIVATE_KEY=your_64_char_hex_key_here

# Settings
TRADING_MODE=dry-run
MIN_PROFIT=0.02
```

### 3. Save and Close
```bash
chmod 600 .env  # Secure permissions
```

---

## ✅ Test Credentials

### Test Kalshi
```bash
cd backend
python test_kalshi_api.py
```

Expected output:
```
✅ API Key found: a1b2c3d4...7890
✅ Private key file exists
✅ Account Balance: $100.00
🎉 SUCCESS! Kalshi API is working!
```

### Test Polymarket
```bash
python test_polymarket_api.py
```

Expected output:
```
✅ Private key found: 1234abcd...ef56
✅ Valid Ethereum private key
💰 USDC Balance: $100.00
🎉 SUCCESS! Polymarket credentials valid!
```

---

## 🚀 Run the Bot

### Dry-Run Mode (Safe Testing)
```bash
python enhanced_arbitrage_bot.py --mode dry-run
```

### Live Trading (After Testing!)
```bash
# Edit .env first
TRADING_MODE=live

# Run
python enhanced_arbitrage_bot.py --mode live
```

---

## 🆘 Quick Troubleshooting

### Kalshi "Invalid API Key"
```bash
# Verify file exists
ls -la ~/.kalshi/private_key.pem

# Check permissions
chmod 600 ~/.kalshi/private_key.pem

# Re-download from Kalshi if needed
```

### Polymarket "Invalid Private Key"
```bash
# Check length (should be 64 chars)
echo "$POLYMARKET_PRIVATE_KEY" | wc -c

# Remove 0x prefix if present
# ❌ 0x1234abcd...
# ✅ 1234abcd...
```

### "No USDC Balance"
```bash
# Check you're on Polygon network (not Ethereum!)
# USDC must be on Polygon (Chain ID 137)
```

### "Module Not Found"
```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 📚 Full Documentation

- **Complete Setup**: [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)
- **Advanced Guide**: [ADVANCED_GUIDE.md](ADVANCED_GUIDE.md)
- **Enhanced Features**: [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)

---

## 💰 Cost Summary

| Item | Cost | One-Time? |
|------|------|-----------|
| **Kalshi Account** | Free | ✅ |
| **MetaMask Wallet** | Free | ✅ |
| **Initial Funds** | $100-200 | ✅ |
| **Trading Fees** | ~7% (Kalshi) | Per trade |
| **Gas Fees** | ~$0.01 (Polygon) | Per trade |
| **Server** | $5/month (AWS) | Recurring |

**Total to start**: ~$100-200 + $5/month

---

## ⚡ Summary

```bash
# 1. Get Kalshi credentials
https://kalshi.com → Settings → API Keys

# 2. Get Polymarket wallet
https://metamask.io → Export Private Key

# 3. Configure bot
cp .env.example .env
nano .env  # Add credentials

# 4. Test
python test_kalshi_api.py
python test_polymarket_api.py

# 5. Run
python enhanced_arbitrage_bot.py --mode dry-run
```

**Done! You're ready to find arbitrage opportunities!** 🎉

---

**⚠️ Remember**:
- Always test in dry-run mode first
- Start with small amounts ($50-100)
- Never share your private keys
- US residents: Check Polymarket TOS compliance
