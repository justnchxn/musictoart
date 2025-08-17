import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if os.getenv("RENDER") is None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
else:
    load_dotenv(PROJECT_ROOT / ".env", override=False)

SPOTIFY_CLIENT_ID    = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "")  
SESSION_SECRET       = os.getenv("SESSION_SECRET", "dev-secret")
ALLOWED_SCOPES       = (os.getenv(
    "ALLOWED_SCOPES",
    "user-top-read user-read-recently-played playlist-read-private"
)).split()

STABILITY_API_KEY    = os.getenv("STABILITY_API_KEY", "")
STABILITY_MODEL      = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")
