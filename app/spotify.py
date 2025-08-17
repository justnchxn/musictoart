import time
import httpx
from fastapi import Request
from itsdangerous import BadSignature

from .auth import signer
from .config import SPOTIFY_CLIENT_ID 

API_BASE = "https://api.spotify.com/v1"

def get_tokens(request: Request):
    """Read signed session cookie and return token dict or None."""
    cookie = request.cookies.get("session")
    if not cookie:
        return None
    try:
        data = signer.loads(cookie)
    except BadSignature:
        return None

    if data.get("expires_at") and int(time.time()) >= int(data["expires_at"]):
        return None
    return data

async def fetch_top(request: Request):
    """Fetch top artists and tracks using the stored access token."""
    tokens = get_tokens(request)
    if not tokens:
        return None

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    async with httpx.AsyncClient(timeout=20) as client:
        a = await client.get(f"{API_BASE}/me/top/artists?limit=20", headers=headers)
        t = await client.get(f"{API_BASE}/me/top/tracks?limit=20", headers=headers)

    if a.status_code != 200 or t.status_code != 200:
        return None

    return {"artists": a.json().get("items", []), "tracks": t.json().get("items", [])}
