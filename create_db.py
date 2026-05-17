import sqlite3
import os
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
        duration_ms INTEGER,
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
        FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
    );
    """)

    conn.commit()

    # ======================================================
    # OPTIONAL SAMPLE DATA (replace with your dataset load)
    # ======================================================

    print("Database created successfully.")

    conn.close()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    DB_PATH = os.path.join(BASE_DIR, "spotify.db")
    main(DB_PATH)
