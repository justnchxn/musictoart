import time
import httpx
from fastapi import Request
from itsdangerous import BadSignature
from .config import SPOTIFY_CLIENT_ID
from .auth import signer

API = "https://api.spotify.com/v1"

async def _authed_client(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    return httpx.AsyncClient(headers=headers, timeout=20)

def get_tokens(request: Request):
    cookie = request.cookies.get("session")
    if not cookie:
        return None
    try:
        return signer.loads(cookie)
    except BadSignature:
        return None

async def fetch_top(request: Request):
    t = get_tokens(request)
    if not t:
        return None
    access = t["access_token"]
    async with await _authed_client(access) as client:
        arts = await client.get(f"{API}/me/top/artists", params={"time_range":"medium_term","limit":50})
        trax = await client.get(f"{API}/me/top/tracks", params={"time_range":"medium_term","limit":50})
        arts.raise_for_status(); trax.raise_for_status()
        return {"artists": arts.json().get("items", []), "tracks": trax.json().get("items", [])}