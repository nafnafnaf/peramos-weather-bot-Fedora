#!/bin/bash

# Deployment script for secured Weather Bot (no hardcoded tokens)
# For Fedora ThinkPad X220

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
IMAGE_NAME="peramos-bot:secured"
CONTAINER_NAME="weather-bot-secured"

echo -e "${BLUE}🔒 Deploying Secured Weather Bot on Fedora ThinkPad${NC}"
echo "================================================"

# Check Docker
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker not running. Please start Docker first${NC}"
    echo "Run: sudo systemctl start docker"
    exit 1
fi

# Get token securely (never store in files)
get_token() {
    echo -e "${YELLOW}🔐 Token Configuration${NC}"
    
    # Check if token is already in environment
    if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${GREEN}✓ Using token from environment${NC}"
        return
    fi
    
    # Try to get from GitHub secrets using gh CLI
    if command -v gh &> /dev/null; then
        echo "Attempting to fetch from GitHub secrets..."
        if gh auth status &> /dev/null 2>&1; then
            TELEGRAM_BOT_TOKEN=$(gh secret view TELEGRAM_BOT_TOKEN --json value -q .value 2>/dev/null)
            if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
                echo -e "${GREEN}✓ Token fetched from GitHub secrets${NC}"
                return
            fi
        fi
    fi
    
    # Manual input as last resort
    echo -e "${YELLOW}Enter your Telegram Bot Token:${NC}"
    echo "(Input will be hidden for security)"
    read -s TELEGRAM_BOT_TOKEN
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${RED}❌ No token provided. Bot cannot start without token.${NC}"
        exit 1
    fi
}

# Stop and remove old containers
cleanup_old() {
    echo -e "${YELLOW}Cleaning up old containers...${NC}"
    
    # Stop and remove both old and new container names
    for container in weather-bot weather-bot-secured weather-bot-secure; do
        if docker ps -a | grep -q $container; then
            docker stop $container 2>/dev/null || true
            docker rm $container 2>/dev/null || true
            echo "  Removed: $container"
        fi
    done
}

# Build secured image
build_image() {
    echo -e "${YELLOW}Building secured image...${NC}"
    
    # Check if app.py has hardcoded token
    if grep -q "AAEkpBMf8xfEgGQHSXSkyqd0QTtcej7SrmQ" app.py 2>/dev/null; then
        echo -e "${RED}⚠️  WARNING: Hardcoded token found in app.py!${NC}"
        echo "The secured version should not contain tokens."
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Build the image
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}✓ Image built: $IMAGE_NAME${NC}"
}

# Run secured container
run_container() {
    echo -e "${YELLOW}Starting secured container...${NC}"
    
    # Get hostname for location
    HOSTNAME=$(hostname)
    
    # Run with token from environment
    docker run -d \
      --name $CONTAINER_NAME \
      --memory="128m" \
      --memory-swap="256m" \
      --cpus="0.5" \
      --restart unless-stopped \
      -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
      -e BOT_LOCATION="$HOSTNAME" \
      $IMAGE_NAME
    
    # Immediately clear token from environment
    unset TELEGRAM_BOT_TOKEN
    
    echo -e "${GREEN}✓ Container started${NC}"
}

# Verify deployment
verify() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    sleep 3
    
    if docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${GREEN}✅ Bot is running successfully!${NC}"
        echo ""
        
        # Show container info
        echo -e "${BLUE}Container Info:${NC}"
        docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
        echo ""
        
        # Show recent logs
        echo -e "${BLUE}Recent Logs:${NC}"
        docker logs $CONTAINER_NAME --tail 5
        echo ""
        
        # Show resource usage
        echo -e "${BLUE}Resource Usage:${NC}"
        docker stats $CONTAINER_NAME --no-stream
        echo ""
        
        # Show commands
        echo -e "${BLUE}Useful Commands:${NC}"
        echo "  View logs:    docker logs -f $CONTAINER_NAME"
        echo "  Check stats:  docker stats $CONTAINER_NAME"
        echo "  Restart:      docker restart $CONTAINER_NAME"
        echo "  Stop:         docker stop $CONTAINER_NAME"
        echo ""
        
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  Secured bot deployed without${NC}"
        echo -e "${GREEN}  any hardcoded tokens! 🔒${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        echo -e "${RED}❌ Bot failed to start${NC}"
        echo "Checking logs for errors..."
        docker logs $CONTAINER_NAME
        exit 1
    fi
}

# Main execution
main() {
    cleanup_old
    get_token
    build_image
    run_container
    verify
}

# Run main function
main