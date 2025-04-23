import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://127.0.0.1:8888/callback"

if not client_id or not client_secret:
    st.error("Missing Spotify credentials. Make sure CLIENT_ID and CLIENT_SECRET are set.")
    st.stop()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = redirect_uri,
        scope = ["user-top-read", "user-library-read", "playlist-read-private", "playlist-read-collaborative"]
    )
)

st.set_page_config(page_title = "Spotify Music Visualiser", page_icon = "musical_note")
st.title("Spotify Music Visualiser")
st.write("Converts Your Music Tastes Into Art")

top_tracks_short = sp.current_user_top_tracks(limit=10, time_range="short_term")
top_tracks_medium = sp.current_user_top_tracks(limit=10, time_range="medium_term")
top_tracks_long = sp.current_user_top_tracks(limit=10, time_range="long_term")

track_ids_short = [track["id"] for track in top_tracks_short["items"]]
track_ids_medium = [track["id"] for track in top_tracks_medium["items"]]
track_ids_long = [track["id"] for track in top_tracks_long["items"]]

audio_features_short = sp.audio_features(track_ids_short)
audio_features_medium = sp.audio_features(track_ids_medium)
audio_features_long = sp.audio_features(track_ids_long)

st.subheader("Audio Feature for Top Tracks")
tab1, tab2, tab3 = st.tabs(["Short Term", "Medium Term", "Long Term"])

with tab1:
    df_short = pd.DataFrame(audio_features_short)
    df_short["track_name"] = [f"{track['name']} - {track['artists'][0]['name']}" for track in top_tracks_short["items"]]
    df_short = df_short[["track_name", "danceability", "energy", "valence"]]
    df_short.set_index("track_name", inplace=True)
    st.bar_chart(df_short)

with tab2:
    df_medium = pd.DataFrame(audio_features_medium)
    df_medium["track_name"] = [track["name"] for track in top_tracks_medium["items"]]
    df_medium = df_medium[["track_name", "danceability", "energy", "valence"]]
    df_medium.set_index("track_name", inplace=True)
    st.bar_chart(df_medium)

with tab3:
    df_long = pd.DataFrame(audio_features_long)
    df_long["track_name"] = [track["name"] for track in top_tracks_long["items"]]
    df_long = df_long[["track_name", "danceability", "energy", "valence"]]
    df_long.set_index("track_name", inplace=True)
    st.bar_chart(df_long)