import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# ----------------------------
# PATHS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spotify.db")
CSV_PATH = os.path.join(BASE_DIR, "spotify_50000.csv")

# ----------------------------
# INIT DB (SAFE - ONLY IF MISSING)
# ----------------------------
def init_db():
    if not os.path.exists(DB_PATH):
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        conn = sqlite3.connect(DB_PATH)

        df.to_sql("tracks", conn, if_exists="replace", index=False)

        conn.close()

init_db()

# ----------------------------
# CONNECTION
# ----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_data(query):
    conn = get_conn()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()

# ----------------------------
# LOAD DATA (RELATIONAL QUERY)
# ----------------------------
def load_tracks():
    query = """
    SELECT
        t.track_id,
        t.track_name,
        a.artist_name,
        g.genre_name,
        t.popularity,
        t.danceability,
        t.energy,
        t.valence,
        t.tempo,
        t.duration_ms
    FROM tracks t
    JOIN artists a ON t.artists = a.artists
    JOIN genres g ON t.genre_id = g.genre_id
    """
    return get_data(query)

df = load_tracks()

# ----------------------------
# UI
# ----------------------------
st.title("Spotify Dashboard (Relational DB)")

st.sidebar.header("Filters")

# ----------------------------
# GENRE FILTER (SAFE)
# ----------------------------
genre_col = "genre_name"

genres = df[genre_col].dropna().unique()
selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + list(genres))

filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df[genre_col] == selected_genre]

# ----------------------------
# KPI METRICS
# ----------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Tracks", len(filtered_df))
col2.metric("Avg Popularity", round(filtered_df["popularity"].mean(), 2))
col3.metric("Avg Tempo", round(filtered_df["tempo"].mean(), 2))

# ----------------------------
# CHARTS
# ----------------------------
st.subheader("Popularity Distribution")

fig1 = px.histogram(filtered_df, x="popularity")
st.plotly_chart(fig1)

st.subheader("Energy vs Danceability")

fig2 = px.scatter(
    filtered_df,
    x="energy",
    y="danceability",
    color="popularity"
)

st.plotly_chart(fig2)

# ----------------------------
# TABLE
# ----------------------------
st.subheader("Raw Data")
st.dataframe(filtered_df)
