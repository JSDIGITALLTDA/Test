#!/bin/bash

# Quick Deploy Script for Polymarket-Kalshi Arbitrage Bot
# Usage: curl -sSL https://raw.githubusercontent.com/.../quick-deploy.sh | bash

set -e

echo "================================================"
echo "  Polymarket-Kalshi Arbitrage Bot Quick Deploy"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Update system
echo -e "${BLUE}[1/6] Updating system...${NC}"
sudo apt update -qq

# Install dependencies
echo -e "${BLUE}[2/6] Installing dependencies...${NC}"
sudo apt install -y git python3 python3-pip nodejs npm > /dev/null 2>&1

# Clone repository
echo -e "${BLUE}[3/6] Cloning repository...${NC}"
cd ~
if [ -d "polymarket-kalshi-btc-arbitrage-bot" ]; then
    cd polymarket-kalshi-btc-arbitrage-bot
    git pull
else
    git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
    cd polymarket-kalshi-btc-arbitrage-bot
fi

# Install Python dependencies
echo -e "${BLUE}[4/6] Installing Python packages...${NC}"
cd backend
pip3 install -q -r requirements.txt
cd ..

# Install Node.js dependencies
echo -e "${BLUE}[5/6] Installing Node.js packages (this may take a minute)...${NC}"
cd frontend
npm install --silent
npm run build > /dev/null 2>&1
cd ..

# Setup and start services
echo -e "${BLUE}[6/6] Setting up services...${NC}"
chmod +x setup-aws.sh
sudo ./setup-aws.sh

echo ""
echo "================================================"
echo -e "${GREEN}  ✓ Deployment Complete!${NC}"
echo "================================================"
