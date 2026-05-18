import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spotify.db")
CSV_PATH = os.path.join(BASE_DIR, "spotify_50000.csv")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    df.to_sql("tracks", conn, if_exists="replace", index=False)

    conn.close()

init_db()

# ----------------------------
# PATH FIX (VERY IMPORTANT)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spotify.db")

# ----------------------------
# DB CONNECTION
# ----------------------------
def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ----------------------------
# LOAD DATA
# ----------------------------
def load_tracks():
    query = "SELECT * FROM tracks"
    return get_data(query)

df = load_tracks()

def get_filtered_tracks(selected_genre, search_text, search_artist, popularity_min):

    query = """
    SELECT
        t.track_name,
        a.artist,
        g.genre_name,
        t.popularity,
        t.danceability,
        t.energy,
        t.valence,
        t.tempo,
        t.duration_ms

    FROM tracks t

    JOIN artists a
        ON t.artist_id = a.artist_id

    JOIN genres g
        ON t.genre_id = g.genre_id

    WHERE t.popularity >= ?
    AND t.track_name LIKE ?
    """

    params = [popularity_min, f"%{search_text}%"]

    if selected_genre != "Todos":
        query += " AND g.genre_name = ?"
        params.append(selected_genre)

    if search_artist.strip() != "":
        query += " AND a.artist LIKE ?"
        params.append(f"%{search_artist}%")

    query += " ORDER BY t.popularity DESC"

    return cached_query(query, tuple(params))
def top_artists_query(selected_genre):

    query = """
    SELECT
        a.artist,
        AVG(t.popularity) AS avg_popularity,
        COUNT(*) AS total_tracks

    FROM tracks t

    JOIN artists a
        ON t.artist_id = a.artist_id

    JOIN genres g
        ON t.genre_id = g.genre_id
    """

    params = []

    if selected_genre != "Todos":
        query += " WHERE g.genre_name = ?"
        params.append(selected_genre)

    query += """
    GROUP BY a.artist
    HAVING COUNT(*) >= 5
    ORDER BY avg_popularity DESC
    LIMIT 10
    """

    return cached_query(query, tuple(params))


def duration_by_genre_query():

    query = """
    SELECT
        g.genre_name,
        AVG(t.duration_ms) / 60000.0 AS avg_minutes

    FROM tracks t

    JOIN genres g
        ON t.genre_id = g.genre_id

    GROUP BY g.genre_name

    ORDER BY avg_minutes DESC

    LIMIT 15
    """

    return cached_query(query)


# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.header("Filtros")

genres_df = load_genres()
genre_list = ["Todos"] + genres_df["genre_name"].tolist()

selected_genre = st.sidebar.selectbox("Género", genre_list)

search_text = st.sidebar.text_input("Buscar canción", "")

search_artist = st.sidebar.text_input("Buscar artista", "")

popularity_min = st.sidebar.slider("Popularidad mínima", 0, 100, 50)


# ----------------------------
# UI
# ----------------------------
st.title("Spotify Dashboard")

st.sidebar.header("Filters")

# Genre filter (safe fallback)
if "genre" in df.columns:
    genres = df["genre"].dropna().unique()
    selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + list(genres))
else:
    selected_genre = "All"

# Filter dataset
filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

# ----------------------------
# KPIs
# ----------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Tracks", len(filtered_df))
col2.metric("Avg Popularity", round(filtered_df["popularity"].mean(), 2))
col3.metric("Avg Tempo", round(filtered_df["tempo"].mean(), 2))

# ----------------------------
# Charts
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
# DATA TABLE
# ----------------------------
st.subheader("Raw Data")
st.dataframe(filtered_df)
