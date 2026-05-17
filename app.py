# ======================================================
# app.py
# ======================================================

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Spotify Analytics Dashboard",
    layout="wide"
)

st.title("🎧 Spotify Analytics Dashboard")
st.markdown("Music analytics using SQLite + Streamlit")


# ======================================================
# DATABASE CONNECTION
# ======================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect(
        "spotify.db",
        check_same_thread=False
    )

conn = get_connection()


# ======================================================
# CACHE SQL QUERIES
# ======================================================

@st.cache_data(ttl=3600)
def cached_query(query, params=None):

    if params is None:
        params = ()

    return pd.read_sql_query(
        query,
        conn,
        params=params
    )


# ======================================================
# LOAD GENRES
# ======================================================

def load_genres():

    query = """
    SELECT genre_name
    FROM genres
    ORDER BY genre_name
    """

    return cached_query(query)


# ======================================================
# FILTERED TRACKS
# ======================================================

def get_filtered_tracks(
    selected_genre,
    search_text,
    search_artist,
    popularity_min
):

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

    params = [
        popularity_min,
        f"%{search_text}%"
    ]

    if selected_genre != "Todos":

        query += """
        AND g.genre_name = ?
        """

        params.append(selected_genre)

    if search_artist.strip() != "":

        query += """
        AND a.artist LIKE ?
        """

        params.append(
            f"%{search_artist}%"
        )

    query += """
    ORDER BY t.popularity DESC
    """

    return cached_query(
        query,
        tuple(params)
    )


# ======================================================
# TOP ARTISTS
# ======================================================

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

        query += """
        WHERE g.genre_name = ?
        """

        params.append(selected_genre)

    query += """
    GROUP BY a.artist
    HAVING COUNT(*) >= 5
    ORDER BY avg_popularity DESC
    LIMIT 10
    """

    return cached_query(
        query,
        tuple(params)
    )


# ======================================================
# DURATION BY GENRE
# ======================================================

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

st.sidebar.header("Filters")

genres_df = load_genres()

genre_list = (
    ["Todos"]
    + genres_df["genre_name"].tolist()
)

selected_genre = st.sidebar.selectbox(
    "Genre",
    genre_list
)

search_text = st.sidebar.text_input(
    "Search track",
    ""
)

search_artist = st.sidebar.text_input(
    "Search artist",
    ""
)

popularity_min = st.sidebar.slider(
    "Minimum popularity",
    0,
    100,
    50
)


# ======================================================
# MAIN FILTERED DATA
# ======================================================

filtered_tracks = get_filtered_tracks(
    selected_genre,
    search_text,
    search_artist,
    popularity_min
)


# ======================================================
# METRICS
# ======================================================

st.subheader("📊 Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Tracks",
    len(filtered_tracks)
)

col2.metric(
    "Average Popularity",
    round(
        filtered_tracks["popularity"].mean(),
        2
    )
    if not filtered_tracks.empty else 0
)

col3.metric(
    "Average Energy",
    round(
        filtered_tracks["energy"].mean(),
        2
    )
    if not filtered_tracks.empty else 0
)


# ======================================================
# DATAFRAME
# ======================================================

st.subheader("📋 Filtered Data")

st.dataframe(
    filtered_tracks.head(50)
)


# ======================================================
# SCATTER PLOT
# ======================================================

st.subheader("⚡ Energy vs Danceability")

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
# TOP ARTISTS CHART
# ======================================================

st.subheader("🔥 Top 10 Artists")

artists_df = top_artists_query(
    selected_genre
)

fig2, ax2 = plt.subplots()

ax2.bar(
    artists_df["artist"],
    artists_df["avg_popularity"]
)

ax2.set_xlabel("Artist")
ax2.set_ylabel("Average Popularity")

plt.xticks(rotation=45)

st.pyplot(fig2)


# ======================================================
# DURATION CHART
# ======================================================

st.subheader("⏱ Average Duration by Genre")

length_df = duration_by_genre_query()

fig3, ax3 = plt.subplots()

ax3.bar(
    length_df["genre_name"],
    length_df["avg_minutes"]
)

ax3.set_xlabel("Genre")
ax3.set_ylabel("Minutes")

plt.xticks(rotation=30)

st.pyplot(fig3)
