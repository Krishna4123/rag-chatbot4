
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Update
from telegram.constants import ParseMode

import asyncio
import threading

from .telegram_bot import TelegramRAGBot

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in .env")
    exit(1)
if not BACKEND_URL:
    logger.error("BACKEND_URL not set in .env")
    exit(1)
if not WEBHOOK_URL:
    logger.error("WEBHOOK_URL not set in .env. Ensure it starts with https://")
    exit(1)

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
bot = TelegramRAGBot(TELEGRAM_BOT_TOKEN, BACKEND_URL)

# Global flag to track if webhook has been set
webhook_set = False

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for the Flask server."""
    return jsonify({'status': 'healthy', 'message': 'Telegram RAG Bot Flask server is running'}), 200

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
async def telegram_webhook():
    """Webhook endpoint for Telegram updates."""
    global webhook_set
    
    # Set webhook on first request if not already set
    if not webhook_set:
        await setup_webhook()
        webhook_set = True
    
    try:
        update = Update.de_json(request.get_json(force=True), bot.application.bot)
        # Process the update using the bot's application
        async with bot.application: # Ensure bot application is properly initialized for async operations
            await bot.application.process_update(update)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

async def setup_webhook():
    """Sets the Telegram webhook at startup."""
    webhook_full_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    logger.info(f"Attempting to set webhook to: {webhook_full_url}")
    async with bot.application.bot: # Use async context manager for bot operations
        success = await bot.application.bot.set_webhook(url=webhook_full_url)
    if success:
        logger.info("Webhook successfully set.")
    else:
        logger.error("Failed to set webhook.")

# The Flask app instance itself is what Gunicorn serves.
# For local testing, you can uncomment the following block:
if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=10000, debug=True)
