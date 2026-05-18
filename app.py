# ======================================================
# IMPORTAR LIBRERÍAS
# ======================================================

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


import os

st.write("DB exists:", os.path.exists("spotify.db"))
st.write("Current working dir:", os.getcwd())
# Load CSV
df = pd.read_csv("spotify_50000.csv")

# Connect (this will overwrite your DB)
conn = sqlite3.connect("spotify.db")
cur = conn.cursor()

# -------------------------
# DROP OLD TABLES (IMPORTANT)
# -------------------------
cur.execute("DROP TABLE IF EXISTS tracks")
cur.execute("DROP TABLE IF EXISTS artists")
cur.execute("DROP TABLE IF EXISTS genres")

# -------------------------
# CREATE TABLES
# -------------------------
cur.execute("""
CREATE TABLE artists (
    artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name TEXT UNIQUE
)
""")

cur.execute("""
CREATE TABLE genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT UNIQUE
)
""")

cur.execute("""
CREATE TABLE tracks (
    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_name TEXT,
    artist_id INTEGER,
    genre_id INTEGER,
    popularity REAL,
    danceability REAL,
    energy REAL,
    valence REAL,
    tempo REAL,
    duration_ms INTEGER,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
)
""")

# -------------------------
# INSERT UNIQUE ARTISTS
# -------------------------
artists = df["artists"].dropna().unique()

artist_map = {}
for a in artists:
    cur.execute("INSERT INTO artists (artist_name) VALUES (?)", (a,))
    artist_map[a] = cur.lastrowid

# -------------------------
# INSERT UNIQUE GENRES
# -------------------------
genres = df["track_genre"].dropna().unique()

genre_map = {}
for g in genres:
    cur.execute("INSERT INTO genres (genre_name) VALUES (?)", (g,))
    genre_map[g] = cur.lastrowid

# -------------------------
# INSERT TRACKS
# -------------------------
for _, row in df.iterrows():
    artist_id = artist_map.get(row["artists"])
    genre_id = genre_map.get(row["track_genre"])

    cur.execute("""
        INSERT INTO tracks (
            track_name,
            artist_id,
            genre_id,
            popularity,
            danceability,
            energy,
            valence,
            tempo,
            duration_ms
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["track_name"],
        artist_id,
        genre_id,
        row["popularity"],
        row["danceability"],
        row["energy"],
        row["valence"],
        row["tempo"],
        row["duration_ms"]
    ))

conn.commit()
conn.close()

st.write("Database created successfully with normalized tables.")





df = pd.read_csv("spotify_50000.csv")

@st.cache_resource
def get_connection():
    return sqlite3.connect("spotify.db", check_same_thread=False)


conn = get_connection()


# ======================================================
# CACHE: QUERIES SQL GENÉRICAS
# ======================================================

@st.cache_data(ttl=3600)
def cached_query(query, params=None):
    if params is None:
        params = ()
    return pd.read_sql_query(query, conn, params=params)


# ======================================================
# CONFIG STREAMLIT
# ======================================================

st.set_page_config(
    page_title="Spotify Analytics Dashboard",
    layout="wide"
)

st.title("🎧 Spotify Analytics Dashboard")
st.markdown("Análisis de música con SQLite + Streamlit")


# ======================================================
# FUNCIONES SQL (USANDO CACHE)
# ======================================================

def load_genres():
    query = """
    SELECT genre_name
    FROM genres
    ORDER BY genre_name
    """
    return cached_query(query)


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


# ======================================================
# DATA PRINCIPAL
# ======================================================

filtered_tracks = get_filtered_tracks(
    selected_genre,
    search_text,
    search_artist,
    popularity_min
)


# ======================================================
# MÉTRICAS
# ======================================================

st.subheader("Resumen")

col1, col2, col3 = st.columns(3)

col1.metric("Canciones", len(filtered_tracks))

col2.metric(
    "Popularidad promedio",
    round(filtered_tracks["popularity"].mean(), 2)
    if not filtered_tracks.empty else 0
)

col3.metric(
    "Energía promedio",
    round(filtered_tracks["energy"].mean(), 2)
    if not filtered_tracks.empty else 0
)


# ======================================================
# DATA PREVIEW
# ======================================================

st.subheader("Datos filtrados")
st.dataframe(filtered_tracks.head(50))


# ======================================================
# SCATTER PLOT
# ======================================================

st.subheader("Energy vs Danceability")

fig1, ax1 = plt.subplots()

if not filtered_tracks.empty:
    ax1.scatter(
        filtered_tracks["energy"],
        filtered_tracks["danceability"]
    )

ax1.set_xlabel("Energy")
ax1.set_ylabel("Danceability")

st.pyplot(fig1)


# ======================================================
# TOP ARTISTS
# ======================================================

st.subheader("Top 10 artistas")

artists_df = top_artists_query(selected_genre)

fig2, ax2 = plt.subplots()

ax2.bar(
    artists_df["artist"],
    artists_df["avg_popularity"]
)

ax2.set_xlabel("Artista")
ax2.set_ylabel("Popularidad")

plt.xticks(rotation=45)

st.pyplot(fig2)


# ======================================================
# DURACIÓN
# ======================================================

st.subheader("⏱ Duración promedio por género")

length_df = duration_by_genre_query()

fig3, ax3 = plt.subplots()

ax3.bar(
    length_df["genre_name"],
    length_df["avg_minutes"]
)

ax3.set_xlabel("Género")
ax3.set_ylabel("Minutos")

plt.xticks(rotation=30)

st.pyplot(fig3)


# ======================================================
# CLOSE (NO NECESARIO CERRAR EN STREAMLIT, PERO SE DEJA)
# ======================================================


conn.close()
