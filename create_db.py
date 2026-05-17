import sqlite3
import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter


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
    # LOAD DATA FROM KAGGLE
    # ======================================================

    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "maharshipandya/-spotify-tracks-dataset",
        "spotify.csv"
    )

    # ======================================================
    # INSERT GENRES
    # ======================================================

    genres = df["track_genre"].dropna().unique()

    for g in genres:
        cursor.execute(
            "INSERT OR IGNORE INTO genres (genre_name) VALUES (?)",
            (g,)
        )

    # ======================================================
    # INSERT ARTISTS
    # ======================================================

    artists = df["artists"].dropna().unique()

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
    # INSERT TRACKS
    # ======================================================

    for _, row in df.iterrows():

        if row["track_genre"] in genre_map and row["artists"] in artist_map:

            cursor.execute("""
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
                artist_map[row["artists"]],
                genre_map[row["track_genre"]],
                row["popularity"],
                row["danceability"],
                row["energy"],
                row["valence"],
                row["tempo"],
                row["duration_ms"]
            ))

    conn.commit()
    conn.close()

    print("Kaggle dataset loaded successfully")
