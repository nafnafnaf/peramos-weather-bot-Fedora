# 🌤️ Peramos Weather Bot

A lightweight Telegram bot that fetches real-time weather data from Nea Peramos weather station with optimized Docker deployment and resource management.

## ✨ Features

- 🌡️ **Real-time Weather Data** - Fetches from penteli.meteo.gr/stations/neaperamos
- 💾 **Smart Caching** - 5-minute cache to reduce API calls
- 🔧 **Memory Management** - Prevents memory leaks with automatic cleanup
- 📊 **Resource Monitoring** - Live RAM usage tracking
- 🐳 **Docker Optimized** - Runs with only 30MB RAM (128MB limit)
- 🔄 **Auto-restart** - Automatically recovers from failures
- 📈 **Status Command** - Monitor bot health and memory usage

## 🚀 Quick Install

### One-Line Installation (Easiest)
```bash
curl -sSL https://raw.githubusercontent.com/nafnafnaf/peramos-weather-bot/main/install.sh | bash
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/nafnafnaf/peramos-weather-bot.git
cd peramos-weather-bot

# Run installer
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Check for Docker and Docker Compose
- ✅ Prompt for your Telegram bot token
- ✅ Build and start the container
- ✅ Show status and logs

## 🛠️ Manual Setup

### Prerequisites
- Docker & Docker Compose installed
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/nafnafnaf/peramos-weather-bot.git
cd peramos-weather-bot
```

2. **Configure bot token:**
```bash
# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```

3. **Build and run:**
```bash
docker-compose up -d --build
```

4. **Check logs:**
```bash
docker logs -f weather-bot
```

## 💬 Bot Commands

| Command | Description |
|---------|-------------|
| Any message | Get current weather data |
| `/start` | Show welcome message |
| `/status` | Display bot memory usage |
| `/help` | Show available commands |

## 📦 Resource Limits

The bot runs efficiently with strict resource limits:

| Resource | Limit | Typical Usage |
|----------|-------|---------------|
| Memory | 128MB max | ~30MB |
| Memory Reservation | 64MB | - |
| Swap | 256MB total | - |
| CPU | 50% of one core | <5% |
| Logs | 10MB x 3 files | Rotated |

## 📁 Project Structure

```
peramos-weather-bot/
├── app.py                 # Bot code with memory management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Deployment with resource limits
├── install.sh           # Automated installer
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Modify Cache Duration

Edit `app.py`:
```python
CACHE_TTL = 300  # Cache duration in seconds (default: 5 minutes)
```

### Adjust Resource Limits

Edit `docker-compose.yml`:
```yaml
mem_limit: 128m          # Maximum memory
memswap_limit: 256m      # Total memory + swap
cpu_shares: 512          # CPU priority
```

## 📊 Monitoring

### View real-time logs:
```bash
docker logs -f weather-bot
```

### Monitor resource usage:
```bash
docker stats weather-bot
```

### Check container health:
```bash
docker ps | grep weather-bot
```

### View memory usage in bot:
Send `/status` to your bot on Telegram

## 🔄 Management Commands

### Stop the bot:
```bash
docker-compose down
```

### Restart the bot:
```bash
docker-compose restart
```

### Update and rebuild:
```bash
git pull
docker-compose up -d --build
```

### Remove completely:
```bash
docker-compose down
docker rmi peramos-weather-bot
```

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check if container is running
docker ps | grep weather-bot

# View error logs
docker logs weather-bot --tail 50

# Restart container
docker-compose restart
```

### High memory usage?
```bash
# Force garbage collection
docker restart weather-bot

# Check for memory leaks
docker stats weather-bot
```

### Invalid token error?
```bash
# Update token in .env file
nano .env

# Restart with new token
docker-compose restart
```

## 🏗️ Architecture

The bot uses several optimization techniques:

1. **Memory Management**
   - Automatic garbage collection
   - BeautifulSoup object cleanup
   - Response caching to reduce scraping

2. **Resource Control**
   - Docker memory limits (128MB)
   - CPU usage restrictions
   - Log rotation to prevent disk fill

3. **Reliability**
   - Auto-restart on failure
   - Error handling and retries
   - Health monitoring

## 📈 Performance

- **Memory**: Stable at ~30MB (vs unlimited growth without optimization)
- **Response Time**: <1s for cached, 2-3s for fresh data
- **Uptime**: 99.9% with auto-restart
- **CPU**: <5% average usage

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Weather data from [Penteli Weather Station](http://penteli.meteo.gr/stations/neaperamos/)
- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Containerized with [Docker](https://www.docker.com/)



--

**Made with ❤️ for real-time weather monitoring**

