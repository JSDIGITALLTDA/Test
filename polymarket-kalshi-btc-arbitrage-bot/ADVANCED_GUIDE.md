# 🚀 Advanced Arbitrage Bot Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Strategy](#core-strategy)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Advanced Features](#advanced-features)
5. [Risk Management](#risk-management)
6. [Going Live](#going-live)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The **Polymarket-Kalshi Arbitrage Bot** is a sophisticated trading system designed to capitalize on pricing inefficiencies between two leading prediction markets.

### What's New in This Version

This enhanced version includes:

✅ **Multi-Market Support** - Trade BTC, sports, politics, and more
✅ **Liquidity Analysis** - Prevent slippage by checking order book depth
✅ **Accurate Fee Calculation** - Kalshi's variable fees are properly accounted for
✅ **Execution Engine** - Two-leg order placement with risk management
✅ **Dry-Run Mode** - Test strategies without risking capital
✅ **Market Mapping** - Intelligent matching of markets across platforms

---

## Core Strategy: Risk-Free Arbitrage

The basic principle is to find a "Yes" on one platform and a "No" on the other where the combined cost is less than $1.00.

### Example Trade

**Market**: "Will BTC be above $95,000 at 3pm?"

| Platform | Side | Price | Fee | Net Price |
|----------|------|-------|-----|-----------|
| Polymarket | Down | $0.48 | $0.00 | **$0.48** |
| Kalshi | Yes | $0.47 | $0.03 | **$0.50** |
| **TOTAL** | | | | **$0.98** |

**Payout**: $1.00 (guaranteed)
**Profit**: $0.02 per contract

### Why This Works

If BTC ends up:
- **Below $95k**: Polymarket "Down" wins → $1.00 payout
- **At/Above $95k**: Kalshi "Yes" wins → $1.00 payout

You win either way! 🎉

---

## Infrastructure Setup

### Prerequisites

| Requirement | Details |
|------------|---------|
| **Python** | 3.9+ |
| **Node.js** | 18+ (for dashboard) |
| **Accounts** | Polymarket + Kalshi accounts |
| **Funding** | USDC on Polygon (Poly), USD (Kalshi) |
| **API Keys** | From both platforms |

### Installation

```bash
# 1. Clone the repository
cd polymarket-kalshi-btc-arbitrage-bot

# 2. Install Python dependencies
cd backend
pip install -r requirements.txt

# 3. Install Node dependencies (for dashboard)
cd ../frontend
npm install

# 4. Configure environment
cd ..
cp .env.example .env
# Edit .env with your credentials
```

### Getting API Credentials

#### Kalshi

1. Go to [Kalshi Settings → API Keys](https://kalshi.com/settings/api-keys)
2. Click **"Create Key"**
3. Download the `.pem` file
4. Copy the **API Key ID**
5. Update `.env`:
   ```bash
   KALSHI_API_KEY=your_api_key_id
   KALSHI_PRIVATE_KEY_PATH=/path/to/kalshi_key.pem
   ```

#### Polymarket

1. Open MetaMask (or your Ethereum wallet)
2. Go to **Settings → Security & Privacy**
3. Click **"Export Private Key"**
4. Copy the private key (without `0x` prefix)
5. Update `.env`:
   ```bash
   POLYMARKET_PRIVATE_KEY=your_private_key
   ```

⚠️ **SECURITY WARNING**: Never share these keys with anyone!

---

## Advanced Features

### 1. Market Mapping System

The bot intelligently matches markets across platforms:

```python
from market_mapper import create_market_mapper, MarketCategory

mapper = create_market_mapper()
mappings = mapper.get_all_mappings(
    poly_markets,
    kalshi_markets,
    categories=[MarketCategory.CRYPTO_PRICE, MarketCategory.SPORTS]
)
```

**Features**:
- ✅ Handles different naming conventions
- ✅ Validates resolution sources (prevents resolution risk)
- ✅ Supports multiple market categories
- ✅ Confidence scoring for matches

### 2. Liquidity Analysis

Before executing a trade, the bot checks order book depth:

```python
from liquidity_analyzer import create_liquidity_analyzer

analyzer = create_liquidity_analyzer(
    min_contracts=100,  # Need at least 100 contracts
    max_slippage=0.005  # Accept max $0.005 slippage
)

poly_liq, kalshi_liq, sufficient = analyzer.check_arbitrage_liquidity(
    poly_token_id="0x123...",
    poly_side="Down",
    kalshi_ticker="INXBTC-23DEC31-T95000",
    kalshi_side="yes",
    desired_size=100
)
```

**Why This Matters**:
- Without liquidity checks, you might see an arb at $0.48 but only 10 contracts are available
- The remaining 990 contracts are at $0.52
- Your average cost becomes $0.52 instead of $0.48 → **Loss!**

### 3. Fee Calculation

Kalshi has a **variable fee structure** based on the contract price:

```python
from fee_calculator import create_fee_calculator

calculator = create_fee_calculator(kalshi_fee_rate=0.07)

# Calculate net price (what you actually pay)
net_price = calculator.get_kalshi_net_price(0.50)
# Returns: 0.528 ($0.50 + $0.028 fee)

# Check if profitable after fees
is_profitable, profit = calculator.is_profitable_after_fees(
    poly_price=0.48,
    kalshi_price=0.50
)
```

**Fee Formula**:
```
Fee = min(price, 1-price) × fee_rate
Net Price = price + fee
```

### 4. Execution Engine

The execution engine handles the critical two-leg trade:

```python
from execution_engine import create_execution_engine

engine = create_execution_engine(dry_run=True)  # Start with dry-run!

result = engine.execute_arbitrage(
    poly_token_id="0x123...",
    poly_side="Down",
    poly_price=0.48,
    kalshi_ticker="INXBTC-23DEC31-T95000",
    kalshi_side="yes",
    kalshi_price=0.50,
    size=100
)
```

**Execution Strategy**:
1. Place the **less liquid** order first (usually Kalshi)
2. Immediately place the second order
3. If second order fails, cancel the first
4. Monitor fills with timeout

---

## Risk Management

### Critical Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Execution Risk** | Leg 1 fills but Leg 2 price moves | Execute less liquid market first, use timeouts |
| **Resolution Risk** | Platforms resolve differently | Only trade markets with same resolution source |
| **Liquidity Risk** | Not enough contracts available | Check order book depth before trading |
| **Fee Miscalculation** | Forgot to include Kalshi fees | Always use `calculate_arbitrage_cost()` |
| **API Failures** | Network issues, rate limits | Implement retries and error handling |

### Safety Checklist

Before going live, ensure:

- [ ] Tested in **dry-run mode** for at least 24 hours
- [ ] Verified API credentials work correctly
- [ ] Set appropriate **MIN_PROFIT** threshold
- [ ] Configured **MAX_TOTAL_EXPOSURE** limit
- [ ] Started with **small position sizes** (10-50 contracts)
- [ ] Have **monitoring and alerts** set up
- [ ] Understand the **tax implications** in your jurisdiction
- [ ] Read both platforms' **Terms of Service**

---

## Going Live

### Step 1: Dry-Run Testing

```bash
cd backend
python enhanced_arbitrage_bot.py --mode dry-run --interval 2
```

Let it run for at least a few hours. Check:
- Are opportunities being detected correctly?
- Are the profit calculations accurate?
- Is the bot handling errors gracefully?

### Step 2: Paper Trading

Fund your accounts with **small amounts**:
- Polymarket: $50 USDC on Polygon
- Kalshi: $50 USD

Enable live mode but with small sizes:

```bash
# Edit .env
TRADING_MODE=live
DEFAULT_TRADE_SIZE=10  # Start with just 10 contracts!
MAX_TOTAL_EXPOSURE=100.00
```

### Step 3: Monitor Closely

For the first week:
- ✅ Check the bot **multiple times per day**
- ✅ Verify trades are executing correctly
- ✅ Track actual profit vs. expected profit
- ✅ Watch for any API errors or failures

### Step 4: Scale Gradually

Once you're confident:
- Increase position sizes slowly (10 → 25 → 50 → 100)
- Add more capital incrementally
- Monitor performance metrics

---

## Running on AWS

For 24/7 operation, deploy to AWS:

```bash
# Quick deploy to AWS Lightsail ($5/month)
curl -sSL https://raw.githubusercontent.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot/main/quick-deploy.sh | bash
```

Or see [QUICK_START.md](QUICK_START.md) and [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## Troubleshooting

### "No opportunities found"

**Possible causes**:
- Markets are efficiently priced (normal!)
- Your `MIN_PROFIT` threshold is too high
- Not enough liquidity in the markets

**Solutions**:
- Lower `MIN_PROFIT` to 0.01 (1 cent)
- Check if markets are active (not paused/settled)
- Try different time of day (more volume during market hours)

### "Execution failed"

**Possible causes**:
- API credentials incorrect
- Insufficient balance
- Network timeout
- Rate limiting

**Solutions**:
```bash
# Check API credentials
python -c "from execution_engine import create_execution_engine; create_execution_engine(dry_run=False)"

# Check balances on both platforms

# Review error logs
tail -f /var/log/arbitrage-bot.log
```

### "Liquidity insufficient"

**Possible causes**:
- Order book is thin
- Your `MIN_CONTRACTS` is too high

**Solutions**:
- Lower `MIN_CONTRACTS` to 25-50
- Trade during high-volume periods
- Focus on major markets (BTC > smaller crypto)

---

## Performance Optimization

### Tips for Better Results

1. **Trade During High Volume**
   - US market hours (9am-4pm ET)
   - Major news events
   - Market expiration times

2. **Focus on Liquid Markets**
   - BTC price markets (hourly, daily)
   - Major sports events (NFL, NBA)
   - Presidential elections

3. **Optimize Fee Structure**
   - Use Safe Wallet on Polymarket (gasless)
   - Check if you qualify for Kalshi fee discounts

4. **Monitor Competitor Activity**
   - If profits suddenly disappear, others may be arbing too
   - Try less popular markets
   - Consider faster execution (lower latency)

---

## Legal & Compliance

⚠️ **IMPORTANT DISCLAIMERS**:

1. **US Trading Restrictions**: Trading on Polymarket from within the US may be restricted. Ensure you comply with local regulations.

2. **Tax Implications**: Arbitrage profits are taxable income. Consult a tax professional.

3. **Terms of Service**: Read and comply with both platforms' ToS. Automated trading may be restricted.

4. **No Financial Advice**: This is educational software. Use at your own risk.

5. **No Guarantees**: "Risk-free" arbitrage is theoretical. Technical failures, API outages, and other issues can cause losses.

---

## Next Steps

1. ✅ Read this guide thoroughly
2. ✅ Run in dry-run mode
3. ✅ Start with small capital
4. ✅ Monitor closely
5. ✅ Scale gradually

**Questions?** See the [main README](README.md) or open an issue on GitHub.

**Good luck, and trade responsibly!** 🚀
