import base64, hashlib, os, time
from itsdangerous import URLSafeSerializer
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, SESSION_SECRET, ALLOWED_SCOPES
import httpx

router = APIRouter()
signer = URLSafeSerializer(SESSION_SECRET, salt="sess")

def _pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode("ascii")
    return verifier, challenge

@router.get("/login")
async def login(request: Request):
    verifier, challenge = _pkce_pair()

    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": " ".join(ALLOWED_SCOPES),
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + "&".join(
        f"{k}={httpx.QueryParams({k: v})[k]}" for k, v in params.items()
    )

    # IMPORTANT: set the cookie on the SAME response you return
    resp = RedirectResponse(auth_url, status_code=302)
    resp.set_cookie(
        "pkce_verifier",
        verifier,
        httponly=True,
        samesite="lax",
        max_age=600,
        path="/",
    )
    return resp


@router.get("/callback")
async def callback(request: Request, code: str = "", error: str = ""):
    if error:
        return RedirectResponse(f"/?error={error}")
    verifier = request.cookies.get("pkce_verifier")
    if not verifier:
        return RedirectResponse("/?error=missing_verifier")

    data = {
        "client_id": SPOTIFY_CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "code_verifier": verifier,
    }
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://accounts.spotify.com/api/token", data=data)
        token_res.raise_for_status()
        tokens = token_res.json()

    # minimal session: store access + obtained_at + expires_in
    tokens["obtained_at"] = int(time.time())
    session_cookie = signer.dumps(tokens)
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("pkce_verifier")
    resp.set_cookie("session", session_cookie, httponly=True, samesite="lax")
    return resp