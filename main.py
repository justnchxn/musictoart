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

st.set_page_config(page_title = "Spotify Music Visualiser", page_icon = "musical_note")
st.title("Spotify Music Visualiser")
st.write("Converts Your Music Tastes Into Art")

top_tracks_short = sp.current_user_top_tracks(limit=10, time_range="short_term")
top_tracks_medium = sp.current_user_top_tracks(limit=10, time_range="medium_term")
top_tracks_long = sp.current_user_top_tracks(limit=10, time_range="long_term")