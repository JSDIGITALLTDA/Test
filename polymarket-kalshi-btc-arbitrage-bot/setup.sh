#!/bin/bash
# Enhanced Arbitrage Bot Setup Script
# This script helps you set up the bot quickly and correctly

set -e  # Exit on error

echo "🤖 Enhanced Arbitrage Bot Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Check if Node.js is installed
echo ""
echo "📋 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"

    # Install frontend dependencies
    echo ""
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Node.js not found. Skipping frontend setup.${NC}"
    echo -e "${YELLOW}   Install Node.js 18+ to run the dashboard.${NC}"
fi

# Setup .env file
echo ""
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file from template${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your API credentials!${NC}"
    echo ""
    echo "   1. Open .env in a text editor"
    echo "   2. Add your Kalshi API key and private key path"
    echo "   3. Add your Polymarket private key"
    echo "   4. Adjust other settings as needed"
    echo ""
else
    echo -e "${YELLOW}⚠️  .env already exists. Not overwriting.${NC}"
fi

# Create data directory
echo ""
echo "📁 Creating data directory..."
mkdir -p data
echo -e "${GREEN}✅ Data directory created${NC}"

# Create logs directory
echo ""
echo "📁 Creating logs directory..."
mkdir -p logs
echo -e "${GREEN}✅ Logs directory created${NC}"

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your credentials:"
echo "   nano .env"
echo ""
echo "2. Test in dry-run mode:"
echo "   source venv/bin/activate"
echo "   cd backend"
echo "   python enhanced_arbitrage_bot.py --mode dry-run"
echo ""
echo "3. Start the API server (optional):"
echo "   python api.py"
echo ""
echo "4. Start the dashboard (optional):"
echo "   cd ../frontend"
echo "   npm run dev"
echo ""
echo "📚 Read ADVANCED_GUIDE.md for detailed instructions!"
echo ""
echo -e "${YELLOW}⚠️  Remember: ALWAYS test in dry-run mode first!${NC}"
echo ""
