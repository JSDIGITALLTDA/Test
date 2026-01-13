# Quick Start Guide - 5 Minutes to Deploy

The **fastest** way to get your arbitrage bot running on AWS.

## Prerequisites
- AWS Account
- Credit card (for AWS billing)
- 5 minutes of time

## Fastest Method: AWS Lightsail

### 1. Create Instance (2 minutes)
1. Go to https://lightsail.aws.amazon.com/
2. Click **"Create instance"**
3. Select:
   - Platform: **Linux/Unix**
   - Blueprint: **Ubuntu 22.04 LTS**
   - Plan: **$5/month** (sufficient for this bot)
4. Name it: `arbitrage-bot`
5. Click **"Create instance"**
6. Wait ~30 seconds for it to start

### 2. Open Firewall (1 minute)
1. Click on your new instance
2. Click **"Networking"** tab
3. Under "IPv4 Firewall", click **"Add rule"**:
   - Application: **Custom**
   - Protocol: **TCP**
   - Port: **3000**
   - Click **"Create"**
4. Add another rule:
   - Application: **Custom**
   - Protocol: **TCP**
   - Port: **8000**
   - Click **"Create"**

### 3. Deploy Bot (2 minutes)
1. Click **"Connect using SSH"** button
2. Copy and paste this ONE command:

```bash
curl -sSL https://raw.githubusercontent.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot/main/quick-deploy.sh | bash
```

Or manually run:

```bash
# Update and install dependencies
sudo apt update && sudo apt install -y git python3 python3-pip nodejs npm

# Clone repository
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot

# Install dependencies
cd backend && pip3 install -r requirements.txt && cd ..
cd frontend && npm install && npm run build && cd ..

# Download and run setup script
chmod +x setup-aws.sh
sudo ./setup-aws.sh
```

### 4. Access Your Bot
1. Go back to Lightsail console
2. Copy your instance's **Public IP**
3. Open in browser:
   - **Dashboard:** `http://YOUR_IP:3000`
   - **API:** `http://YOUR_IP:8000/arbitrage`

## Done! 🎉

Your bot is now running 24/7 and monitoring for arbitrage opportunities.

---

## Alternative: One-Line Docker Deploy

If you prefer Docker:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# Deploy bot
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot
docker-compose up -d
```

---

## Useful Commands

```bash
# Check if services are running
sudo systemctl status arbitrage-backend
sudo systemctl status arbitrage-frontend

# View logs
sudo journalctl -u arbitrage-backend -f
sudo journalctl -u arbitrage-frontend -f

# Restart services
sudo systemctl restart arbitrage-backend
sudo systemctl restart arbitrage-frontend

# Stop services
sudo systemctl stop arbitrage-backend arbitrage-frontend
```

---

## Costs

| Service | Cost | Why Choose It |
|---------|------|---------------|
| **Lightsail $5** | $5/month | Simplest, cheapest, perfect for this bot |
| **Lightsail $10** | $10/month | More RAM, faster performance |
| **EC2 t3.micro** | ~$7.50/month | More control, slightly cheaper |

**Recommendation:** Start with Lightsail $5/month. It's more than enough.

---

## Troubleshooting

**Can't access dashboard?**
- Check firewall rules in Lightsail
- Make sure you're using `http://` not `https://`
- Try `http://YOUR_IP:3000` directly

**Services not running?**
```bash
sudo systemctl restart arbitrage-backend arbitrage-frontend
sudo journalctl -u arbitrage-backend -n 50
```

**Want to stop the bot?**
```bash
sudo systemctl stop arbitrage-backend arbitrage-frontend
```

---

## Next Steps

- ✅ Monitor the dashboard for opportunities
- Consider setting up alerts (email/Slack)
- Optional: Add a domain name and HTTPS
- Optional: Set up monitoring with CloudWatch

For more detailed instructions, see [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)
