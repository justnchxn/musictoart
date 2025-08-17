import base64
import hashlib
import os
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
import httpx

from .config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, SESSION_SECRET, ALLOWED_SCOPES
from itsdangerous import URLSafeSerializer, BadSignature
from .config import SESSION_SECRET

signer = URLSafeSerializer(SESSION_SECRET, salt="spotify-session")
router = APIRouter()


def _pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b"=").decode("utf-8")
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("utf-8")
    )
    return verifier, challenge

@router.get("/login")
async def login(request: Request):
    verifier, challenge = _pkce_pair()

    redirect_uri = SPOTIFY_REDIRECT_URI or str(request.url_for("callback"))
    print("DEBUG redirect_uri being used:", redirect_uri)

    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(ALLOWED_SCOPES),
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)

    resp = RedirectResponse(auth_url, status_code=302)

    import os
    is_prod = os.getenv("RENDER") is not None 
    resp.set_cookie(
        "pkce_verifier",
        verifier,
        httponly=True,
        samesite="lax",
        secure=is_prod, 
        max_age=600,
        path="/",
    )

    return resp

@router.get("/callback")
async def callback(request: Request, code: str = "", error: str = ""):
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify error: {error}")

    verifier = request.cookies.get("pkce_verifier")
    if not verifier:
        raise HTTPException(status_code=400, detail="Missing PKCE verifier cookie")

    redirect_uri = SPOTIFY_REDIRECT_URI or str(request.url_for("callback"))

    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "client_id": SPOTIFY_CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": verifier,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Spotify token exchange failed: {resp.text}")

        token_data = resp.json()
        import time
        expires_at = int(time.time()) + int(token_data.get("expires_in", 3600))

        session_payload = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "scope": token_data.get("scope", ""),
            "token_type": token_data.get("token_type", "Bearer"),
        }

        cookie_val = signer.dumps(session_payload)

        redir = RedirectResponse("/", status_code=302)
        redir.set_cookie(
            "session", cookie_val,
            httponly=True, samesite="lax", secure=False, 
            max_age=60*60*24*7, path="/"
        )
        return redir
        
    return token_data
