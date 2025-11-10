import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from typing import Callable

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, chat_id: int = None):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.chat_id = chat_id
        self.check_callback = None
        
    def set_check_callback(self, callback: Callable):
        self.check_callback = callback
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.chat_id is None:
            self.chat_id = update.effective_chat.id
            logger.info(f"Chat ID set to: {self.chat_id}")
        
        await update.message.reply_text(
            "🎵 *Discogs Wantlist Monitor Bot*\n\n"
            "I'll notify you when items from your Discogs wantlist become available for sale!\n\n"
            "*Commands:*\n"
            "/start - Start the bot\n"
            "/status - Check bot status\n"
            "/check - Manually check wantlist now\n"
            "/test - Send a test notification\n"
            "/help - Show this help message\n\n"
            f"Monitoring is active. Checking every {context.bot_data.get('interval', 30)} minutes.",
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from database import Database
        db = Database()
        seen_count = db.get_seen_listings_count()
        
        await update.message.reply_text(
            f"✅ *Bot Status*\n\n"
            f"🔍 Monitoring: Active\n"
            f"📊 Listings tracked: {seen_count}\n"
            f"⏱ Check interval: {context.bot_data.get('interval', 30)} minutes\n"
            f"💬 Chat ID: {update.effective_chat.id}",
            parse_mode='Markdown'
        )
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔍 Checking wantlist now...")
        
        if self.check_callback:
            new_listings = await self.check_callback()
            
            if new_listings == 0:
                await update.message.reply_text("✅ No new listings found.")
            else:
                await update.message.reply_text(f"✅ Found and sent {new_listings} new listing(s)!")
        else:
            await update.message.reply_text("❌ Check function not available.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start_command(update, context)
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🧪 *Test Notification*\n\n"
            "✅ Success\\! The bot can send you messages\\.\n\n"
            "This confirms that:\n"
            "• Your Telegram connection is working\n"
            "• Notifications will be delivered\n"
            "• The bot is monitoring your wantlist\n\n"
            "You'll receive notifications like this when new vinyl records from your wantlist are listed for sale\\!",
            parse_mode='MarkdownV2'
        )
        logger.info(f"Test notification sent to chat {update.effective_chat.id}")
    
    async def send_notification(self, message: str):
        if self.chat_id:
            try:
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                logger.info("Notification sent successfully")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        else:
            logger.warning("No chat ID set. Cannot send notification.")
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("check", self.check_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        logger.info("Bot handlers registered")
    
    def run(self):
        self.setup_handlers()
        logger.info("Starting Telegram bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
