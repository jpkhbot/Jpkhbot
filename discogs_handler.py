from discogs_api import search, get_release

# exemple d'utilisation
def find_release(title):
    results = search(title, qtype="release", per_page=5)
    return results.get("results", [])
import logging
from typing import List, Dict
import time

logger = logging.getLogger(__name__)


class DiscogsHandler:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.client = discogs_client.Client('DiscogerBot/1.0', user_token=token)
        logger.info(f"Discogs client initialized for user: {username}")

    def get_wantlist(self) -> List[Dict]:
        try:
            user = self.client.user(self.username)
            wantlist = []
            
            logger.info(f"Fetching wantlist for {self.username}...")
            
            for item in user.wantlist:
                release = item.release
                wantlist_item = {
                    'release_id': str(release.id),
                    'artist': release.artists[0].name if release.artists else 'Unknown',
                    'title': release.title,
                    'year': getattr(release, 'year', 'N/A'),
                    'url': release.url,
                    'type': 'release'
                }
                wantlist.append(wantlist_item)
                time.sleep(0.5)
            
            logger.info(f"Found {len(wantlist)} items in wantlist")
            return wantlist
            
        except Exception as e:
            logger.error(f"Error fetching wantlist: {e}")
            return []

    def get_marketplace_listings(self, release_id: str) -> List[Dict]:
        try:
            release = self.client.release(release_id)
            listings = []
            
            logger.debug(f"Checking marketplace for release {release_id}: {release.title}")
            
            try:
                for listing in release.marketplace.listings:
                    listing_data = {
                        'listing_id': str(listing.id),
                        'release_id': release_id,
                        'price': f"{listing.price.value} {listing.price.currency}",
                        'condition': listing.condition,
                        'sleeve_condition': getattr(listing, 'sleeve_condition', 'N/A'),
                        'seller_username': listing.seller.username,
                        'seller_rating': listing.seller.rating,
                        'ships_from': getattr(listing, 'ships_from', 'N/A'),
                        'comments': getattr(listing, 'comments', ''),
                        'url': listing.url,
                        'posted': str(getattr(listing, 'posted', 'N/A'))
                    }
                    listings.append(listing_data)
                    
            except Exception as e:
                logger.debug(f"No marketplace listings or error: {e}")
            
            logger.debug(f"Found {len(listings)} listings for release {release_id}")
            return listings
            
        except Exception as e:
            logger.error(f"Error fetching marketplace listings for {release_id}: {e}")
            return []

    def get_release_info(self, release_id: str) -> Dict:
        try:
            release = self.client.release(release_id)
            return {
                'artist': release.artists[0].name if release.artists else 'Unknown',
                'title': release.title,
                'year': getattr(release, 'year', 'N/A'),
                'url': release.url
            }
        except Exception as e:
            logger.error(f"Error fetching release info for {release_id}: {e}")
            return {}
