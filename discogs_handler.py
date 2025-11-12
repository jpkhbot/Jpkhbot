# discogs_handler.py
import os
import requests

BASE_URL = "https://can01.safelinks.protection.outlook.com/?url=https%3A%2F%2Fapi.discogs.com%2F&data=05%7C02%7Cjean-pierre.khazzaka%40stanislas.qc.ca%7C266398b764364046014f08de2220128d%7Ca7378fe7e83e47d79eb25163dc14739f%7C0%7C0%7C638985718331598609%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=VD%2F8nG3uihPlo3h91UfKyuGHh0VeBg54L3hedlG45J0%3D&reserved=0"
TOKEN = os.getenv("DISCOGS_USER_TOKEN")

HEADERS = {
    "User-Agent": "JPDiscogsBot/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Discogs token={TOKEN}"


def search_release(query):
    """Recherche de release"""
    params = {"q": query, "type": "release", "per_page": 5}
    resp = requests.get(f"{BASE_URL}/database/search", headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("results", [])


def get_release_info(release_id):
    """Détails d’une release"""
    resp = requests.get(f"{BASE_URL}/releases/{release_id}", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def format_release_info(data):
    """Mise en forme du texte"""
    title = data.get("title", "Unknown")
    artists = ", ".join(a["name"] for a in data.get("artists", []))
    year = data.get("year", "N/A")
    genres = ", ".join(data.get("genres", []))
    return f"🎵 {title}\n👤 {artists}\n📀 {year} • {genres}"
