import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_url = "http://localhost:5000"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_url = redirect_url,
        scope = ["user-top-read", "user-library-read", "playlist-read-private", "playlist-read-collaborative"]
    )
)