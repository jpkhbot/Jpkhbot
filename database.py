import sqlite3
import json
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "discoger.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                release_id TEXT NOT NULL,
                listing_id TEXT NOT NULL,
                price TEXT,
                condition TEXT,
                seller_username TEXT,
                listing_url TEXT,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(release_id, listing_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wantlist_cache (
                release_id TEXT PRIMARY KEY,
                artist TEXT,
                title TEXT,
                release_url TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def is_listing_seen(self, release_id: str, listing_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM seen_listings 
            WHERE release_id = ? AND listing_id = ?
        """, (release_id, listing_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

    def mark_listing_seen(self, release_id: str, listing_id: str, 
                         price: str = None, condition: str = None,
                         seller_username: str = None, listing_url: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO seen_listings 
                (release_id, listing_id, price, condition, seller_username, listing_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (release_id, listing_id, price, condition, seller_username, listing_url))
            
            conn.commit()
            logger.debug(f"Marked listing {listing_id} for release {release_id} as seen")
        except Exception as e:
            logger.error(f"Error marking listing as seen: {e}")
        finally:
            conn.close()

    def get_seen_listings_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM seen_listings")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def cache_wantlist_item(self, release_id: str, artist: str, title: str, release_url: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO wantlist_cache 
                (release_id, artist, title, release_url, last_checked)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (release_id, artist, title, release_url))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error caching wantlist item: {e}")
        finally:
            conn.close()

    def get_cached_wantlist_item(self, release_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT artist, title, release_url 
            FROM wantlist_cache 
            WHERE release_id = ?
        """, (release_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'artist': result[0],
                'title': result[1],
                'release_url': result[2]
            }
        return None
