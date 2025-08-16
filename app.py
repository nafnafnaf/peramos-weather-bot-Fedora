import os
import gc
import sys
import time
import logging
from datetime import datetime
import telepot
from telepot.loop import MessageLoop
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup as soup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7162260320:AAEkpBMf8xfEgGQHSXSkyqd0QTtcej7SrmQ')
WEATHER_URL = "http://penteli.meteo.gr/stations/neaperamos/"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Cache
weather_cache = {'data': None, 'timestamp': 0}
CACHE_TTL = 300  # 5 minutes

def get_memory_mb():
    """Get memory usage in MB"""
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    except:
        return 0

def scrape_weather_data():
    """Scrape weather data with caching"""
    # Check cache
    if weather_cache['data'] and (time.time() - weather_cache['timestamp'] < CACHE_TTL):
        cached_data = weather_cache['data']
        # Add current memory usage to cached data
        mem = get_memory_mb()
        if "📡 ThinkpadX220" in cached_data:
            cached_data = cached_data.replace("📡 ThinkpadX220", f"📡 Thinkpad X220 | RAM: {mem:.1f}MB")
        return cached_data
    
    try:
        headers = {'User-Agent': USER_AGENT}
        req = Request(WEATHER_URL, headers=headers)
        response = urlopen(req, timeout=10)
        page = response.read()
        response.close()
        
        page_soup = soup(page, "html.parser")
        
        text_labels = []
        values = []
        
        for tag in page_soup.find_all("div", {"class": "lleft"}):
            label = tag.get_text(strip=True).encode('ascii', errors='ignore').decode()
            if label:
                text_labels.append(label)
        
        for tag in page_soup.find_all("div", {"class": "lright"}):
            value = tag.get_text(strip=True)
            if value:
                values.append(value)
        
        if not text_labels or not values:
            return "⚠️ No weather data available"
        
        result = "🌤️ Weather Station: Nea Peramos\n"
        result += "=" * 30 + "\n"
        for label, value in zip(text_labels, values):
            result += f"📊 {label}: {value}\n"
        result += "=" * 30 + "\n"
        result += f"🕐 {datetime.now().strftime('%H:%M:%S')}\n"
        
        # Add memory usage to the output
        mem = get_memory_mb()
        result += f"📡  ThinkpadX220| RAM: {mem:.1f}MB"
        
        # Update cache
        weather_cache['data'] = result
        weather_cache['timestamp'] = time.time()
        
        # Cleanup
        page_soup.decompose()
        gc.collect()
        
        return result
        
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        mem = get_memory_mb()
        return f"❌ Unable to fetch weather data\n📡 ThinkpadX220 | RAM: {mem:.1f}MB"

def handle(msg):
    """Handle messages"""
    try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        logger.info(f"Message from {chat_id}, Memory: {get_memory_mb():.1f}MB")
        
        if content_type == 'text':
            text = msg.get('text', '').lower().strip()
            
            if text == '/start':
                bot.sendMessage(chat_id, "👋 Welcome! Send any message for weather data\n/status - Check bot status")
            elif text == '/status':
                mem = get_memory_mb()
                bot.sendMessage(chat_id, f"🤖 Bot Status\n📊 Memory: {mem:.1f}MB")
            else:
                data = scrape_weather_data()
                bot.sendMessage(chat_id, data)
        
        # Cleanup
        msg = None
        if get_memory_mb() > 100:
            gc.collect()
            
    except Exception as e:
        logger.error(f"Handle error: {e}")

# Main
try:
    bot = telepot.Bot(TOKEN)
    bot_info = bot.getMe()
    logger.info(f"Bot started: @{bot_info['username']}")
    MessageLoop(bot, handle).run_as_thread()
    logger.info(f'Bot listening... Initial memory: {get_memory_mb():.1f}MB')
    
    while True:
        time.sleep(60)
        if int(time.time()) % 300 == 0:  # Every 5 minutes
            gc.collect()
            logger.info(f"Memory: {get_memory_mb():.1f}MB")
            
except Exception as e:
    logger.error(f"Bot failed to start: {e}")
    sys.exit(1)