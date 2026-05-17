import os
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# ======================================================
# PATHS
# ======================================================

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "spotify.db")


# ======================================================
# FORCE DB BUILD IF MISSING OR EMPTY
# ======================================================

def ensure_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='tracks';
    """)

    exists = cursor.fetchone()
    conn.close()

    if not exists:
        st.info("Building database from CSV...")

        import create_db
        create_db.main(DB_PATH)

        st.success("Database ready.")


ensure_database()


# ======================================================
# STREAMLIT CONFIG
# ======================================================

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

st.title("Spotify Analytics Dashboard")


# ======================================================
# CONNECTION
# ======================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()


# ======================================================
# QUERY FUNCTION
# ======================================================

@st.cache_data(ttl=3600)
def query(sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)


# ======================================================
# LOAD DATA
# ======================================================

def load_genres():
    return query("SELECT genre_name FROM genres ORDER BY genre_name")


# ======================================================
# FILTER TRACKS
# ======================================================

def get_tracks(genre, text, artist, pop):

    sql = """
    SELECT t.track_name, a.artist, g.genre_name,
           t.popularity, t.energy, t.danceability
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    JOIN genres g ON t.genre_id = g.genre_id
    WHERE t.popularity >= ?
    AND t.track_name LIKE ?
    """

    params = [pop, f"%{text}%"]

    if genre != "Todos":
        sql += " AND g.genre_name = ?"
        params.append(genre)

    if artist:
        sql += " AND a.artist LIKE ?"
        params.append(f"%{artist}%")

    sql += " ORDER BY t.popularity DESC"

    return query(sql, tuple(params))


# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.header("Filters")

genres_df = load_genres()

genre_list = ["Todos"] + genres_df["genre_name"].tolist()

genre = st.sidebar.selectbox("Genre", genre_list)

text = st.sidebar.text_input("Track")

artist = st.sidebar.text_input("Artist")

pop = st.sidebar.slider("Popularity", 0, 100, 50)


# ======================================================
# DATA
# ======================================================

df = get_tracks(genre, text, artist, pop)


# ======================================================
# METRICS
# ======================================================

st.subheader("Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Tracks", len(df))
c2.metric("Avg Popularity", round(df["popularity"].mean(), 2) if not df.empty else 0)
c3.metric("Avg Energy", round(df["energy"].mean(), 2) if not df.empty else 0)


# ======================================================
# TABLE
# ======================================================

st.dataframe(df.head(50))


# ======================================================
# CHART
# ======================================================

st.subheader("Energy vs Danceability")

fig, ax = plt.subplots()

if not df.empty:
    ax.scatter(df["energy"], df["danceability"])

ax.set_xlabel("Energy")
ax.set_ylabel("Danceability")

st.pyplot(fig)
