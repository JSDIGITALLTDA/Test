#!/bin/bash

set -e

echo "========================================="
echo "Polymarket-Kalshi Arbitrage Bot Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current user
CURRENT_USER=${SUDO_USER:-$USER}
HOME_DIR=$(eval echo ~$CURRENT_USER)
BOT_DIR="$HOME_DIR/polymarket-kalshi-btc-arbitrage-bot"

echo -e "${YELLOW}Setting up arbitrage bot for user: $CURRENT_USER${NC}"
echo -e "${YELLOW}Bot directory: $BOT_DIR${NC}"
echo ""

# Update system
echo -e "${GREEN}[1/7] Updating system...${NC}"
apt update && apt upgrade -y

# Install system dependencies
echo -e "${GREEN}[2/7] Installing system dependencies...${NC}"
apt install -y git python3 python3-pip nodejs npm nginx curl

# Check if bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    echo -e "${GREEN}[3/7] Cloning repository...${NC}"
    cd "$HOME_DIR"
    sudo -u $CURRENT_USER git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
else
    echo -e "${GREEN}[3/7] Repository already exists, skipping clone...${NC}"
fi

# Install Python dependencies
echo -e "${GREEN}[4/7] Installing Python dependencies...${NC}"
cd "$BOT_DIR/backend"
sudo -u $CURRENT_USER pip3 install -r requirements.txt

# Install Node.js dependencies
echo -e "${GREEN}[5/7] Installing Node.js dependencies...${NC}"
cd "$BOT_DIR/frontend"
sudo -u $CURRENT_USER npm install

# Build frontend
echo -e "${GREEN}[5.5/7] Building frontend...${NC}"
sudo -u $CURRENT_USER npm run build

# Setup systemd services
echo -e "${GREEN}[6/7] Setting up systemd services...${NC}"

# Update service files with correct user and paths
sed "s|User=ubuntu|User=$CURRENT_USER|g" "$BOT_DIR/backend-service.service" | \
sed "s|/home/ubuntu|$HOME_DIR|g" > /etc/systemd/system/arbitrage-backend.service

sed "s|User=ubuntu|User=$CURRENT_USER|g" "$BOT_DIR/frontend-service.service" | \
sed "s|/home/ubuntu|$HOME_DIR|g" > /etc/systemd/system/arbitrage-frontend.service

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable arbitrage-backend.service
systemctl enable arbitrage-frontend.service

# Start services
echo -e "${GREEN}[7/7] Starting services...${NC}"
systemctl start arbitrage-backend.service
systemctl start arbitrage-frontend.service

# Wait a moment for services to start
sleep 3

# Check status
echo ""
echo "========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================="
echo ""

# Get public IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "YOUR_SERVER_IP")

echo "Service Status:"
systemctl status arbitrage-backend.service --no-pager -l || true
echo ""
systemctl status arbitrage-frontend.service --no-pager -l || true

echo ""
echo "========================================="
echo -e "${GREEN}Access Your Bot:${NC}"
echo "========================================="
echo ""
echo "Dashboard: http://$PUBLIC_IP:3000"
echo "Backend API: http://$PUBLIC_IP:8000/arbitrage"
echo ""
echo "To view logs:"
echo "  Backend:  sudo journalctl -u arbitrage-backend -f"
echo "  Frontend: sudo journalctl -u arbitrage-frontend -f"
echo ""
echo "To restart services:"
echo "  sudo systemctl restart arbitrage-backend"
echo "  sudo systemctl restart arbitrage-frontend"
echo ""
echo -e "${GREEN}Happy arbitrage hunting! 🚀${NC}"
