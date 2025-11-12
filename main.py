import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import Config
from database import Database
from discogs_handler import search_release, get_release_info, format_release_info
from bot import TelegramBot
from keep_alive import keep_alive
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class DiscogerBot:
    def __init__(self):
        Config.validate()
        
        self.db = Database()
        self.discogs = DiscogsHandler(Config.DISCOGS_TOKEN, Config.DISCOGS_USERNAME)
        self.bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
        self.scheduler = AsyncIOScheduler()
        
        self.bot.app.bot_data['interval'] = Config.CHECK_INTERVAL_MINUTES
        
    async def check_wantlist(self) -> int:
        logger.info("Starting wantlist check...")
        new_listings_count = 0
        
        try:
            wantlist = await asyncio.to_thread(self.discogs.get_wantlist)
            
            if not wantlist:
                logger.warning("Wantlist is empty or could not be fetched")
                return 0
            
            logger.info(f"Checking {len(wantlist)} items in wantlist...")
            
            for item in wantlist:
                release_id = item['release_id']
                
                await asyncio.to_thread(
                    self.db.cache_wantlist_item,
                    release_id,
                    item['artist'],
                    item['title'],
                    item['url']
                )
                
                listings = await asyncio.to_thread(
                    self.discogs.get_marketplace_listings, 
                    release_id
                )
                
                for listing in listings:
                    listing_id = listing['listing_id']
                    
                    is_seen = await asyncio.to_thread(
                        self.db.is_listing_seen, 
                        release_id, 
                        listing_id
                    )
                    
                    if not is_seen:
                        await self.send_listing_notification(item, listing)
                        
                        await asyncio.to_thread(
                            self.db.mark_listing_seen,
                            release_id,
                            listing_id,
                            listing['price'],
                            listing['condition'],
                            listing['seller_username'],
                            listing['url']
                        )
                        
                        new_listings_count += 1
                        await asyncio.sleep(1)
                
                await asyncio.sleep(2)
            
            logger.info(f"Wantlist check complete. Found {new_listings_count} new listings.")
            
        except Exception as e:
            logger.error(f"Error during wantlist check: {e}")
        
        return new_listings_count
    
    def escape_markdown(self, text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))
    
    async def send_listing_notification(self, item: dict, listing: dict):
        artist = self.escape_markdown(item['artist'])
        title = self.escape_markdown(item['title'])
        year = self.escape_markdown(item.get('year', 'N/A'))
        price = self.escape_markdown(listing['price'])
        condition = self.escape_markdown(listing['condition'])
        sleeve = self.escape_markdown(listing.get('sleeve_condition', 'N/A'))
        seller = self.escape_markdown(listing['seller_username'])
        rating = self.escape_markdown(listing.get('seller_rating', 'N/A'))
        ships = self.escape_markdown(listing.get('ships_from', 'N/A'))
        
        message = (
            f"🎵 *NEW LISTING FOUND\\!*\n\n"
            f"*Artist:* {artist}\n"
            f"*Title:* {title}\n"
            f"*Year:* {year}\n\n"
            f"💰 *Price:* {price}\n"
            f"📀 *Condition:* {condition}\n"
            f"📦 *Sleeve:* {sleeve}\n"
            f"👤 *Seller:* {seller} \\({rating}%\\)\n"
            f"🌍 *Ships from:* {ships}\n\n"
        )
        
        if listing.get('comments'):
            comments_raw = listing['comments'][:200]
            comments = self.escape_markdown(comments_raw)
            ellipsis = '\\.\\.\\.' if len(listing['comments']) > 200 else ''
            message += f"💬 *Comments:* {comments}{ellipsis}\n\n"
        
        message += f"🔗 [View Listing]({listing['url']})\n"
        message += f"🔗 [View Release]({item['url']})"
        
        await self.bot.send_notification(message)
    
    def schedule_checks(self):
        self.scheduler.add_job(
            self.check_wantlist,
            trigger=IntervalTrigger(minutes=Config.CHECK_INTERVAL_MINUTES),
            id='wantlist_check',
            name='Check Discogs Wantlist',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduled wantlist checks every {Config.CHECK_INTERVAL_MINUTES} minutes")
    
    async def initial_check(self):
        await asyncio.sleep(5)
        logger.info("Running initial wantlist check...")
        await self.check_wantlist()
    
    async def async_run(self):
        logger.info("=== Discoger Bot Starting ===")
        logger.info(f"Discogs Username: {Config.DISCOGS_USERNAME}")
        logger.info(f"Check Interval: {Config.CHECK_INTERVAL_MINUTES} minutes")
        
        self.bot.set_check_callback(self.check_wantlist)
        self.bot.setup_handlers()
        
        self.schedule_checks()
        
        asyncio.create_task(self.initial_check())
        
        async with self.bot.app:
            await self.bot.app.start()
            await self.bot.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            
            logger.info("Bot is running. Press Ctrl+C to stop.")
            
            try:
                await asyncio.Event().wait()
            except (KeyboardInterrupt, SystemExit):
                logger.info("Shutting down...")
            finally:
                await self.bot.app.updater.stop()
                await self.bot.app.stop()


if __name__ == "__main__":
    try:
        from telegram import Update
        
        keep_alive()
        logger.info("Keep-alive web server started on port 3000")
        
        bot = DiscogerBot()
        asyncio.run(bot.async_run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
