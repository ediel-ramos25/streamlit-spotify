import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="Spotify Dashboard", layout="wide")
st.title("🎧 Spotify Analytics Dashboard")

# ======================================================
# CONNECTION (SAFE)
# ======================================================
@st.cache_resource
def get_connection():
    db_path = os.path.join(os.getcwd(), "spotify.db")
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

# ======================================================
# DEBUG (REMOVE LATER IF YOU WANT)
# ======================================================
st.write("DB exists:", os.path.exists("spotify.db"))

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
st.write("Tables:", tables)

# ======================================================
# QUERY FUNCTION
# ======================================================
def run_query(query, params=()):
    return pd.read_sql(query, conn, params=params)

# ======================================================
# LOAD FILTER OPTIONS
# ======================================================
def load_genres():
    return run_query("SELECT genre_name FROM genres ORDER BY genre_name")

# ======================================================
# MAIN FILTER QUERY
# ======================================================
def get_filtered_tracks(genre, search_text, search_artist, min_pop):

    query = """
    SELECT
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
    JOIN artists a ON t.artist_id = a.artist_id
    JOIN genres g ON t.genre_id = g.genre_id
    WHERE t.popularity >= ?
    AND t.track_name LIKE ?
    """

    params = [min_pop, f"%{search_text}%"]

    if genre != "Todos":
        query += " AND g.genre_name = ?"
        params.append(genre)

    if search_artist.strip():
        query += " AND a.artist_name LIKE ?"
        params.append(f"%{search_artist}%")

    query += " ORDER BY t.popularity DESC"

    return run_query(query, tuple(params))

# ======================================================
# TOP ARTISTS
# ======================================================
def top_artists(genre):

    query = """
    SELECT
        a.artist_name,
        AVG(t.popularity) AS avg_popularity,
        COUNT(*) AS total_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    JOIN genres g ON t.genre_id = g.genre_id
    """

    params = []

    if genre != "Todos":
        query += " WHERE g.genre_name = ?"
        params.append(genre)

    query += """
    GROUP BY a.artist_name
    HAVING COUNT(*) >= 5
    ORDER BY avg_popularity DESC
    LIMIT 10
    """

    return run_query(query, tuple(params))

# ======================================================
# DURATION BY GENRE
# ======================================================
def duration_by_genre():

    query = """
    SELECT
        g.genre_name,
        AVG(t.duration_ms)/60000.0 AS avg_minutes
    FROM tracks t
    JOIN genres g ON t.genre_id = g.genre_id
    GROUP BY g.genre_name
    ORDER BY avg_minutes DESC
    LIMIT 15
    """

    return run_query(query)

# ======================================================
# SIDEBAR
# ======================================================
genres_df = load_genres()
genre_list = ["Todos"] + genres_df["genre_name"].tolist()

selected_genre = st.sidebar.selectbox("Género", genre_list)
search_text = st.sidebar.text_input("Buscar canción")
search_artist = st.sidebar.text_input("Buscar artista")
min_pop = st.sidebar.slider("Popularidad mínima", 0, 100, 50)

# ======================================================
# DATA
# ======================================================
df = get_filtered_tracks(selected_genre, search_text, search_artist, min_pop)

# ======================================================
# METRICS
# ======================================================
st.subheader("Resumen")

col1, col2, col3 = st.columns(3)

col1.metric("Canciones", len(df))

col2.metric(
    "Popularidad promedio",
    round(df["popularity"].mean(), 2) if not df.empty else 0
)

col3.metric(
    "Energía promedio",
    round(df["energy"].mean(), 2) if not df.empty else 0
)

# ======================================================
# TABLE
# ======================================================
st.subheader("Datos filtrados")
st.dataframe(df.head(50))

# ======================================================
# SCATTER
# ======================================================
st.subheader("Energy vs Danceability")

fig1, ax1 = plt.subplots()

if not df.empty:
    ax1.scatter(df["energy"], df["danceability"])

ax1.set_xlabel("Energy")
ax1.set_ylabel("Danceability")

st.pyplot(fig1)

# ======================================================
# TOP ARTISTS
# ======================================================
st.subheader("Top 10 artistas")

artist_df = top_artists(selected_genre)

fig2, ax2 = plt.subplots()

ax2.bar(artist_df["artist_name"], artist_df["avg_popularity"])
plt.xticks(rotation=45)

st.pyplot(fig2)

# ======================================================
# DURATION
# ======================================================
st.subheader("Duración promedio por género")

dur_df = duration_by_genre()

fig3, ax3 = plt.subplots()

ax3.bar(dur_df["genre_name"], dur_df["avg_minutes"])
plt.xticks(rotation=30)

st.pyplot(fig3)
