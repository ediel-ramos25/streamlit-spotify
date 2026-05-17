import sqlite3


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
    conn.close()

    print("Database created successfully")
