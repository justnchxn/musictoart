import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://127.0.0.1:8888/callback"

# Validate credentials
if not client_id or not client_secret:
    st.error("Missing Spotify credentials. Make sure CLIENT_ID and CLIENT_SECRET are set.")
    st.stop()

# Set up Spotify client with safe caching and forced login refresh
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-top-read",
        # scope=["user-top-read", "user-library-read", "playlist-read-private", "playlist-read-collaborative"],
        show_dialog=True,
        cache_path=".cache"
    )
)

# Streamlit UI
st.set_page_config(page_title="Spotify Music Visualiser", page_icon="🎵")
st.title("Spotify Music Visualiser")
st.write("🎨 Converts Your Music Tastes Into Art")

# Fetch user display name for a quick check
try:
    user = sp.current_user()
    st.success(f"Logged in as: {user['display_name']}")
except Exception as e:
    st.error(f"Failed to fetch user info: {e}")
    st.stop()

# Fetch top tracks
top_tracks_short = sp.current_user_top_tracks(limit=10, time_range="short_term")
top_tracks_medium = sp.current_user_top_tracks(limit=10, time_range="medium_term")
top_tracks_long = sp.current_user_top_tracks(limit=10, time_range="long_term")

# Display tracks for debugging
st.write(f"Top Short-Term Tracks: {top_tracks_short}")
st.write(f"Top Medium-Term Tracks: {top_tracks_medium}")
st.write(f"Top Long-Term Tracks: {top_tracks_long}")

# Extract valid track IDs
def extract_ids(tracks):
    return [track["id"] for track in tracks["items"] if track["id"]]

track_ids_short = extract_ids(top_tracks_short)
track_ids_medium = extract_ids(top_tracks_medium)
track_ids_long = extract_ids(top_tracks_long)

# Log track IDs for debugging
st.write(f"Track IDs (short term): {track_ids_short}")
st.write(f"Track IDs (medium term): {track_ids_medium}")
st.write(f"Track IDs (long term): {track_ids_long}")

# Handle no tracks found scenario
if not track_ids_short or not track_ids_medium or not track_ids_long:
    st.warning("No top tracks found for the user.")
    st.stop()

# Check availability of tracks by fetching each one manually
def check_track_availability(track_ids):
    available_tracks = []
    for track_id in track_ids:
        try:
            track_info = sp.track(track_id)
            available_tracks.append(track_info)
            logging.info(f"Track found: {track_info['name']}")
        except Exception as e:
            logging.error(f"Error fetching track info for {track_id}: {e}")
    return available_tracks

available_tracks_short = check_track_availability(track_ids_short)
available_tracks_medium = check_track_availability(track_ids_medium)
available_tracks_long = check_track_availability(track_ids_long)

# Safe wrapper for audio features
def safe_audio_features(sp, ids, label=""):
    try:
        logging.info(f"Fetching audio features for {label} tracks: {ids}")
        response = sp.audio_features(ids)
        logging.debug(f"API Response: {response}")
        return response
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"Spotify API error for {label} tracks: {e}")
        return []

audio_features_short = safe_audio_features(sp, track_ids_short, "short-term")
audio_features_medium = safe_audio_features(sp, track_ids_medium, "medium-term")
audio_features_long = safe_audio_features(sp, track_ids_long, "long-term")

# Display feature charts
st.subheader("🎧 Audio Features of Your Top Tracks")
tab1, tab2, tab3 = st.tabs(["Short Term", "Medium Term", "Long Term"])

def create_chart(tab, features, tracks, label):
    with tab:
        if not features:
            st.warning(f"No audio features available for {label}.")
            return
        df = pd.DataFrame(features)
        df["track_name"] = [f"{track['name']} - {track['artists'][0]['name']}" for track in tracks["items"]]
        df = df[["track_name", "danceability", "energy", "valence"]]
        df.set_index("track_name", inplace=True)
        st.bar_chart(df)

create_chart(tab1, audio_features_short, top_tracks_short, "short term")
create_chart(tab2, audio_features_medium, top_tracks_medium, "medium term")
create_chart(tab3, audio_features_long, top_tracks_long, "long term")
