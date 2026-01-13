# AWS Deployment Guide for Polymarket-Kalshi Arbitrage Bot

This guide will help you deploy the arbitrage bot to AWS and run it 24/7.

## Option 1: AWS Lightsail (Recommended - Easiest)

**Cost:** ~$5-10/month for a small instance

### Step 1: Create a Lightsail Instance

1. Go to [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Click **"Create instance"**
3. Choose:
   - **Platform:** Linux/Unix
   - **Blueprint:** OS Only → Ubuntu 22.04 LTS
   - **Instance plan:** $5/month (1 GB RAM, 1 vCPU) or $10/month (2 GB RAM)
4. Name your instance: `arbitrage-bot`
5. Click **"Create instance"**

### Step 2: Configure Firewall

1. Click on your instance
2. Go to **"Networking"** tab
3. Add these firewall rules:
   - **Application:** Custom
   - **Protocol:** TCP
   - **Port:** 3000 (for frontend dashboard)
   - Click **"Create"**
   - Add another:
   - **Protocol:** TCP
   - **Port:** 8000 (for backend API)
   - Click **"Create"**

### Step 3: Connect and Deploy

1. Click **"Connect using SSH"** in the Lightsail console
2. Run the deployment script:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y git python3 python3-pip nodejs npm nginx

# Clone the repository
cd ~
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot

# Install Python dependencies
cd backend
pip3 install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
npm run build
cd ..

# Download and run the setup script
curl -o setup-aws.sh https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/setup-aws.sh
chmod +x setup-aws.sh
sudo ./setup-aws.sh
```

### Step 4: Access Your Bot

1. Get your instance's public IP from Lightsail console
2. Open in browser:
   - **Dashboard:** `http://YOUR_IP:3000`
   - **API:** `http://YOUR_IP:8000/arbitrage`

---

## Option 2: AWS EC2 (More Control)

**Cost:** ~$8-15/month (t2.micro or t3.micro)

### Step 1: Launch EC2 Instance

1. Go to [AWS EC2 Console](https://console.aws.amazon.com/ec2/)
2. Click **"Launch Instance"**
3. Configure:
   - **Name:** arbitrage-bot
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance type:** t2.micro (free tier) or t3.micro
   - **Key pair:** Create new or use existing
   - **Network settings:**
     - Allow SSH (port 22) from your IP
     - Allow Custom TCP (port 3000) from anywhere
     - Allow Custom TCP (port 8000) from anywhere
4. Click **"Launch instance"**

### Step 2: Connect via SSH

```bash
# Replace with your key and instance IP
ssh -i "your-key.pem" ubuntu@your-instance-ip
```

### Step 3: Deploy the Bot

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y git python3 python3-pip nodejs npm nginx

# Clone repository
cd ~
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot

# Install Python dependencies
cd backend
pip3 install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
npm run build
cd ..

# Setup services to run on startup
sudo cp backend-service.service /etc/systemd/system/arbitrage-backend.service
sudo cp frontend-service.service /etc/systemd/system/arbitrage-frontend.service

# Start services
sudo systemctl daemon-reload
sudo systemctl enable arbitrage-backend
sudo systemctl enable arbitrage-frontend
sudo systemctl start arbitrage-backend
sudo systemctl start arbitrage-frontend

# Check status
sudo systemctl status arbitrage-backend
sudo systemctl status arbitrage-frontend
```

---

## Option 3: Docker Deployment (Most Portable)

### Step 1: Create Docker Files (Already provided in repo)

### Step 2: Deploy to EC2/Lightsail

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Clone and build
git clone https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot.git
cd polymarket-kalshi-btc-arbitrage-bot

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## Monitoring and Maintenance

### Check Service Status
```bash
sudo systemctl status arbitrage-backend
sudo systemctl status arbitrage-frontend
```

### View Logs
```bash
# Backend logs
sudo journalctl -u arbitrage-backend -f

# Frontend logs
sudo journalctl -u arbitrage-frontend -f
```

### Restart Services
```bash
sudo systemctl restart arbitrage-backend
sudo systemctl restart arbitrage-frontend
```

### Update the Bot
```bash
cd ~/polymarket-kalshi-btc-arbitrage-bot
git pull
sudo systemctl restart arbitrage-backend
sudo systemctl restart arbitrage-frontend
```

---

## Cost Breakdown

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **Lightsail** | 1 GB RAM, 1 vCPU | $5 |
| **Lightsail** | 2 GB RAM, 1 vCPU | $10 |
| **EC2 t2.micro** | 1 GB RAM, 1 vCPU | $8.50 |
| **EC2 t3.micro** | 2 GB RAM, 2 vCPU | $7.50 |

**Recommendation:** Start with **Lightsail $5/month** plan. It's simple and sufficient.

---

## Security Best Practices

1. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Enable firewall:**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 3000/tcp
   sudo ufw allow 8000/tcp
   sudo ufw enable
   ```

3. **Use SSH keys** instead of passwords

4. **Consider adding Nginx reverse proxy** for HTTPS (optional)

---

## Troubleshooting

### Bot not starting?
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check Node version
node --version  # Should be 14+

# Reinstall dependencies
cd ~/polymarket-kalshi-btc-arbitrage-bot/backend
pip3 install -r requirements.txt

cd ../frontend
npm install
```

### Can't access dashboard?
- Check firewall rules in AWS console
- Verify services are running: `sudo systemctl status arbitrage-*`
- Check instance public IP is correct

### API errors?
- APIs may be rate-limited
- Check logs: `sudo journalctl -u arbitrage-backend -n 50`

---

## Next Steps

1. ✅ Deploy to AWS
2. ✅ Access dashboard at `http://YOUR_IP:3000`
3. Monitor for arbitrage opportunities
4. Optional: Set up domain name and HTTPS
5. Optional: Configure email/Slack alerts for opportunities
