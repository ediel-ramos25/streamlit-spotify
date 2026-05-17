import os
import sqlite3
import pandas as pd


def main(db_path):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ======================================================
    # CREATE TABLES
    # ======================================================

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS genres (
        genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre_name TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS tracks (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_name TEXT,
        artist_id INTEGER,
        genre_id INTEGER,
        popularity INTEGER,
        danceability REAL,
        energy REAL,
        valence REAL,
        tempo REAL,
        duration_ms INTEGER
    );
    """)

    conn.commit()

    # ======================================================
    # SAFE CSV PATH (IMPORTANT FIX)
    # ======================================================

    BASE_DIR = os.path.dirname(__file__)
    csv_path = os.path.join(BASE_DIR, "spotify_50000.csv")

    df = pd.read_csv(csv_path)

    df = df.dropna(subset=["track_name", "artists", "track_genre"])

    print("ROWS LOADED:", len(df))

    # ======================================================
    # INSERT GENRES
    # ======================================================

    genres = df["track_genre"].unique()

    for g in genres:
        cursor.execute(
            "INSERT OR IGNORE INTO genres (genre_name) VALUES (?)",
            (g,)
        )

    # ======================================================
    # INSERT ARTISTS
    # ======================================================

    artists = df["artists"].unique()

    for a in artists:
        cursor.execute(
            "INSERT OR IGNORE INTO artists (artist) VALUES (?)",
            (a,)
        )

    conn.commit()

    # ======================================================
    # MAP IDS
    # ======================================================

    genre_map = dict(cursor.execute("SELECT genre_name, genre_id FROM genres"))
    artist_map = dict(cursor.execute("SELECT artist, artist_id FROM artists"))

    # ======================================================
    # BULK INSERT TRACKS (FAST + SAFE)
    # ======================================================

    track_rows = []

    for _, row in df.iterrows():

        g_id = genre_map.get(row["track_genre"])
        a_id = artist_map.get(row["artists"])

        if g_id is not None and a_id is not None:

            track_rows.append((
                row["track_name"],
                a_id,
                g_id,
                int(row["popularity"]) if pd.notna(row["popularity"]) else 0,
                float(row["danceability"]) if pd.notna(row["danceability"]) else 0,
                float(row["energy"]) if pd.notna(row["energy"]) else 0,
                float(row["valence"]) if pd.notna(row["valence"]) else 0,
                float(row["tempo"]) if pd.notna(row["tempo"]) else 0,
                int(row["duration_ms"]) if pd.notna(row["duration_ms"]) else 0
            ))

    cursor.executemany("""
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
    """, track_rows)

    conn.commit()
    conn.close()

    print("DATABASE CREATED SUCCESSFULLY")


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    DB_PATH = os.path.join(BASE_DIR, "spotify.db")
    main(DB_PATH)
