# discogs_api.py
# Petit wrapper minimal pour appeler l'API Discogs sans dépendance externe
# Utilise requests, tu dois définir DISCOGS_USER_TOKEN dans .env

import os
import requests

DISCOGS_BASE = "https://can01.safelinks.protection.outlook.com/?url=https%3A%2F%2Fapi.discogs.com%2F&data=05%7C02%7Cjean-pierre.khazzaka%40stanislas.qc.ca%7Cfe5812c3811e428809b008de220a0e55%7Ca7378fe7e83e47d79eb25163dc14739f%7C0%7C0%7C638985623803409039%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=qel%2F6wFNg70SJRjBH6Z97ZPyskMsOwvIdIpY1WlyDoc%3D&reserved=0"
TOKEN = os.getenv("DISCOGS_USER_TOKEN")  # mets ton token dans .env

HEADERS = {
    "User-Agent": "JPBot/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Discogs token={TOKEN}"

def search(query, qtype="release", page=1, per_page=10):
    """
    search(query, qtype='release'|'artist'|'label')
    Retourne JSON des résultats.
    """
    params = {
        "q": query,
        "type": qtype,
        "page": page,
        "per_page": per_page,
    }
    url = f"{DISCOGS_BASE}/database/search"
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def get_release(release_id):
    url = f"{DISCOGS_BASE}/releases/{release_id}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()
