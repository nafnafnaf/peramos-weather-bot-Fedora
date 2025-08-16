#!/bin/bash

# Simple deployment for Fedora ThinkPad with Rancher Desktop

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Deploying Weather Bot on Fedora ThinkPad"

# Check Docker/Rancher
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker not running. Start Rancher Desktop first${NC}"
    exit 1
fi

# Create .env if needed
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    read -p "Enter your Telegram Bot Token: " BOT_TOKEN
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
BOT_LOCATION=Fedora-ThinkPad
EOF
else
    # Update location if not set
    if ! grep -q "BOT_LOCATION" .env; then
        echo "BOT_LOCATION=Fedora-ThinkPad" >> .env
    fi
fi

# Stop old container
docker stop weather-bot 2>/dev/null || true
docker rm weather-bot 2>/dev/null || true

# Build and run
echo -e "${YELLOW}Building container...${NC}"
docker build -t peramos-weather-bot .

echo -e "${YELLOW}Starting bot...${NC}"
docker run -d \
  --name weather-bot \
  --memory="128m" \
  --memory-swap="256m" \
  --cpus="0.5" \
  --restart unless-stopped \
  --env-file .env \
  peramos-weather-bot

# Check status
sleep 3
if docker ps | grep -q weather-bot; then
    echo -e "${GREEN}✅ Bot is running!${NC}"
    echo ""
    docker logs weather-bot --tail 5
    echo ""
    echo "Commands:"
    echo "  View logs:  docker logs -f weather-bot"
    echo "  Check RAM:  docker stats weather-bot"
    echo "  Restart:    docker restart weather-bot"
    echo "  Stop:       docker stop weather-bot"
else
    echo -e "${RED}❌ Failed to start${NC}"
    docker logs weather-bot
fi