# 🤖 Polymarket-Kalshi BTC Arbitrage Bot

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14+-black.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)

**Real-time arbitrage detection for the Bitcoin 1-Hour Price market between Polymarket and Kalshi.**

## 🚀 Overview

The **Polymarket-Kalshi BTC Arbitrage Bot** is a powerful tool designed to monitor and identify risk-free arbitrage opportunities in the **Bitcoin 1-Hour Price** market between two of the world's leading prediction markets: **Polymarket** and **Kalshi**.

By leveraging real-time data from Polymarket's CLOB (Central Limit Order Book) and Kalshi's API, this bot calculates the combined cost of opposing positions (e.g., "Yes" on Kalshi + "Down" on Polymarket) for the same hourly expiration. If the total cost is less than $1.00, a risk-free profit opportunity exists.

This project includes:
-   **Python Backend**: Fast and efficient data fetching and arbitrage logic using FastAPI.
-   **Next.js Dashboard**: A beautiful, real-time UI built with shadcn/ui to visualize market data and opportunities.

> 📚 **Learn the Theory**: Read our detailed [Arbitrage Thesis](thesis.md) to understand the mathematics behind risk-free profits in binary option markets.

## ✨ Features

### Core Features
-   **Real-Time Monitoring**: Fetches live prices every second.
-   **Smart Matching**: Automatically matches Polymarket events with their corresponding Kalshi markets.
-   **Arbitrage Detection**: Instantly identifies "risk-free" trades where the total cost < $1.00.
-   **Visual Dashboard**:
    -   **Live Updates**: See prices change in real-time.
    -   **Best Opportunity Highlight**: Prominently displays the most profitable trade.
    -   **Visual Cost Bars**: Quickly assess the cost breakdown of each strategy.
-   **Comprehensive Analysis**: Checks multiple strategies (Poly Down + Kalshi Yes, Poly Up + Kalshi No).

### 🚀 Enhanced Features (New!)
-   **Multi-Market Support**: Trade BTC, sports, politics, and more
-   **Liquidity Analysis**: Check order book depth to prevent slippage
-   **Accurate Fee Calculation**: Kalshi's variable fees properly accounted for
-   **Execution Engine**: Two-leg order placement with risk management
-   **Dry-Run Mode**: Test strategies without risking capital
-   **Market Mapping**: Intelligent matching across platforms with resolution validation

> 📚 **New to the bot?** See [API_QUICKSTART.md](API_QUICKSTART.md) for a 5-minute setup guide!

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, Uvicorn, Requests
-   **Frontend**: TypeScript, Next.js, Tailwind CSS, shadcn/ui, Lucide React

## 🔑 API Setup

Before running the bot, you need API credentials from both platforms:

### Quick Start (5 minutes)
📖 See **[API_QUICKSTART.md](API_QUICKSTART.md)** for a fast setup guide

### Detailed Guide
📖 See **[API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)** for complete instructions

### What You Need:
1. **Kalshi Account**
   - API Key ID
   - Private Key (.pem file)
   - Funded account ($100+)

2. **Polymarket Wallet**
   - MetaMask wallet
   - Ethereum private key
   - USDC on Polygon ($100+)

### Test Your Credentials:
```bash
cd backend
python test_kalshi_api.py      # Test Kalshi connection
python test_polymarket_api.py  # Test Polymarket connection
```

## 📦 Installation

### Prerequisites
-   Python 3.9+
-   Node.js 18+
-   npm or yarn

### 1. Clone the Repository
```bash
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot
```

### 2. Setup Backend
Navigate to the `backend` directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Frontend
Navigate to the `frontend` directory and install dependencies:
```bash
cd ../frontend
npm install
```

## 🚀 Usage

To run the full application, you need to start both the backend and frontend servers.

### 1. Start Backend API
In the `backend` directory:
```bash
python3 api.py
```
The API will start at `http://localhost:8000`.

### 2. Start Frontend Dashboard
In the `frontend` directory:
```bash
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

## 📊 How It Works

1.  **Data Ingestion**: The bot fetches the latest "Bitcoin Up or Down" hourly market from Polymarket and searches for the corresponding markets on Kalshi.
2.  **Normalization**: Prices are normalized to a standard probability format (0.00 - 1.00).
3.  **Comparison**: The bot compares the "Price to Beat" (Strike Price) on Polymarket with Kalshi's strike prices.
    -   If `Poly Strike > Kalshi Strike`: Checks `Poly Down + Kalshi Yes`.
    -   If `Poly Strike < Kalshi Strike`: Checks `Poly Up + Kalshi No`.
4.  **Calculation**: It sums the cost of the two legs. If `Total Cost < $1.00`, it's an arbitrage opportunity!

## 📚 Documentation

Comprehensive guides for all aspects of the bot:

| Guide | Description | Time |
|-------|-------------|------|
| **[API_QUICKSTART.md](API_QUICKSTART.md)** | Get API credentials in 5 minutes | ⚡ 5 min |
| **[API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)** | Complete API setup with troubleshooting | 📖 15 min |
| **[QUICK_START.md](QUICK_START.md)** | Deploy to AWS in 5 minutes | 🚀 5 min |
| **[ADVANCED_GUIDE.md](ADVANCED_GUIDE.md)** | Deep dive into strategy and features | 🎓 30 min |
| **[ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)** | Technical docs for all modules | 🔧 20 min |
| **[AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)** | Detailed AWS deployment guide | ☁️ 20 min |
| **[thesis.md](thesis.md)** | Mathematical theory of arbitrage | 📐 10 min |

### Quick Links
- 🆘 **Troubleshooting**: See [API_SETUP_GUIDE.md#troubleshooting](API_SETUP_GUIDE.md#troubleshooting)
- 🔒 **Security**: See [ADVANCED_GUIDE.md#risk-management](ADVANCED_GUIDE.md#risk-management)
- 💰 **Cost Breakdown**: See [QUICK_START.md#costs](QUICK_START.md#costs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## ⚠️ Disclaimer

This software is for educational purposes only.

- **No Financial Advice**: This is not financial advice. Use at your own risk.
- **Trading Risks**: All trading involves risk. Past performance doesn't guarantee future results.
- **Compliance**: Ensure you comply with local regulations. Polymarket may be restricted in certain jurisdictions.
- **No Guarantees**: "Risk-free" arbitrage is theoretical. Technical failures and market conditions can cause losses.

Always test thoroughly in dry-run mode before risking real capital.
