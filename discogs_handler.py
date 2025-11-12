# discogs_handler.py
# Version simplifiée sans python-discogs-client
# Utilise l'API Discogs directement via HTTP (requests)
# Nécessite : DISCOGS_USER_TOKEN dans .env

import os
import requests

DISCOGS_BASE = "https://can01.safelinks.protection.outlook.com/?url=https%3A%2F%2Fapi.discogs.com%2F&data=05%7C02%7Cjean-pierre.khazzaka%40stanislas.qc.ca%7Ca655dfef514043e50cb708de220b4b79%7Ca7378fe7e83e47d79eb25163dc14739f%7C0%7C0%7C638985629089224858%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=KHgl7%2F27AFLHTgZt1Etk7I7%2BK6oGMo%2BF4es96788rvA%3D&reserved=0"
TOKEN = os.getenv("DISCOGS_USER_TOKEN")

HEADERS = {
    "User-Agent": "JPBot/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Discogs token={TOKEN}"


def search_release(query, per_page=5):
    """Recherche un album ou single par titre"""
    params = {"q": query, "type": "release", "per_page": per_page}
    r = requests.get(f"{DISCOGS_BASE}/database/search", headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])


def get_release_info(release_id):
    """Retourne les détails d'une release spécifique"""
    r = requests.get(f"{DISCOGS_BASE}/releases/{release_id}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def format_release_info(data):
    """Formate les infos pour affichage"""
    title = data.get("title", "Unknown title")
    artists = ", ".join([a["name"] for a in data.get("artists", [])]) if "artists" in data else "Unknown artist"
    year = data.get("year", "N/A")
    genres = ", ".join(data.get("genres", [])) if "genres" in data else "N/A"
    country = data.get("country", "Unknown")
    return f"🎵 *{title}*\n👤 {artists}\n📀 {year} • {genres}\n🌍 {country}"
