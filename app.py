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

# Choose layout style (1-5)
LAYOUT_STYLE = int(os.environ.get('LAYOUT_STYLE', '1'))

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

def format_layout_1(text_labels, values):
    """Ultra Minimal - Just data"""
    result = "**Nea Peramos**\n\n"
    for label, value in zip(text_labels, values):
        result += f"{label}: {value}\n"
    result += f"\n{datetime.now().strftime('%H:%M')}"
    return result

def format_layout_2(text_labels, values):
    """Clean Dots"""
    result = "**NEA PERAMOS**\n"
    result += "• " + "• " * 10 + "\n\n"
    for label, value in zip(text_labels, values):
        result += f"• {label}: `{value}`\n"
    result += "\n• " + "• " * 10 + "\n"
    result += f"{datetime.now().strftime('%H:%M')} | {get_memory_mb():.0f}MB"
    return result

def format_layout_3(text_labels, values):
    """Compact Lines"""
    result = "```\n"
    result += "NEA PERAMOS WEATHER\n"
    result += "─" * 20 + "\n"
    for label, value in zip(text_labels, values):
        padding = " " * (15 - len(label))
        result += f"{label}{padding} {value}\n"
    result += "─" * 20 + "\n"
    result += f"{datetime.now().strftime('%H:%M:%S')}\n"
    result += "```"
    return result

def format_layout_4(text_labels, values):
    """Single Line Summary (Most Minimal)"""
    # Pick most important values
    temp = next((v for l, v in zip(text_labels, values) if 'temp' in l.lower()), 'N/A')
    humid = next((v for l, v in zip(text_labels, values) if 'humid' in l.lower()), 'N/A')
    wind = next((v for l, v in zip(text_labels, values) if 'wind' in l.lower() and 'speed' in l.lower()), 'N/A')
    
    result = f"**Peramos** {datetime.now().strftime('%H:%M')}\n"
    result += f"🌡 {temp} • 💧 {humid} • 💨 {wind}\n"
    result += f"\n_Full: /details_"
    return result

def format_layout_5(text_labels, values):
    """Modern Minimal"""
    result = f"**PERAMOS** • {datetime.now().strftime('%H:%M')}\n\n"
    
    # Group by importance
    for label, value in zip(text_labels, values):
        if any(x in label.lower() for x in ['temp', 'humid', 'wind', 'press']):
            result += f"**{label}**\n{value}\n\n"
        else:
            result += f"{label}: {value}\n"
    
    location = os.environ.get('BOT_LOCATION', 'X220')
    result += f"\n_{location} • {get_memory_mb():.0f}MB_"
    return result

def scrape_weather_data(detailed=False):
    """Scrape weather data with caching"""
    # Check cache
    if not detailed and weather_cache['data'] and (time.time() - weather_cache['timestamp'] < CACHE_TTL):
        return weather_cache['data']
    
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
            return "No data available"
        
        # Choose layout based on style
        if LAYOUT_STYLE == 1:
            result = format_layout_1(text_labels, values)
        elif LAYOUT_STYLE == 2:
            result = format_layout_2(text_labels, values)
        elif LAYOUT_STYLE == 3:
            result = format_layout_3(text_labels, values)
        elif LAYOUT_STYLE == 4:
            if detailed:
                result = format_layout_2(text_labels, values)  # Show full for /details
            else:
                result = format_layout_4(text_labels, values)
        else:
            result = format_layout_5(text_labels, values)
        
        # Update cache
        weather_cache['data'] = result
        weather_cache['timestamp'] = time.time()
        
        # Cleanup
        page_soup.decompose()
        gc.collect()
        
        return result
        
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        return f"Connection error\n{datetime.now().strftime('%H:%M')}"

def handle(msg):
    """Handle messages"""
    try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        logger.info(f"Message from {chat_id}, Memory: {get_memory_mb():.1f}MB")
        
        if content_type == 'text':
            text = msg.get('text', '').lower().strip()
            
            if text == '/start':
                bot.sendMessage(chat_id, "Send any message for weather\n/style - Change layout")
            elif text == '/status':
                mem = get_memory_mb()
                bot.sendMessage(chat_id, f"Memory: {mem:.0f}MB\nStyle: {LAYOUT_STYLE}")
            elif text == '/style':
                styles = """Choose layout style:
                
1 - Ultra Minimal
2 - Clean Dots
3 - Compact Lines
4 - Single Line
5 - Modern Minimal

Send: /style1, /style2, etc."""
                bot.sendMessage(chat_id, styles)
            elif text.startswith('/style'):
                try:
                    global LAYOUT_STYLE
                    LAYOUT_STYLE = int(text[-1])
                    weather_cache['data'] = None  # Clear cache
                    bot.sendMessage(chat_id, f"Style changed to {LAYOUT_STYLE}")
                except:
                    bot.sendMessage(chat_id, "Invalid style")
            elif text == '/details':
                data = scrape_weather_data(detailed=True)
                bot.sendMessage(chat_id, data, parse_mode='Markdown')
            else:
                data = scrape_weather_data()
                bot.sendMessage(chat_id, data, parse_mode='Markdown')
        
        # Cleanup
        msg = None
        if get_memory_mb() > 100:
            gc.collect()
            
    except Exception as e:
        logger.error(f"Handle error: {e}")

# Main
start_time = time.time()
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
logger.info(f'Bot started, listening... Initial memory: {get_memory_mb():.1f}MB')

while True:
    time.sleep(60)
    if int(time.time()) % 300 == 0:  # Every 5 minutes
        gc.collect()
        logger.info(f"Memory: {get_memory_mb():.1f}MB")