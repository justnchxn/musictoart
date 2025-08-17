# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

SPOTIFY_CLIENT_ID    = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/callback")
SESSION_SECRET       = os.getenv("SESSION_SECRET", "dev-secret")

# bring this back:
ALLOWED_SCOPES = os.getenv(
    "ALLOWED_SCOPES",
    "user-top-read user-read-recently-played playlist-read-private"
).split()

# (optional, used by /api/generate)
STABILITY_API_KEY    = os.getenv("STABILITY_API_KEY", "")
STABILITY_MODEL      = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")
