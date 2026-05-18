import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "spotify_50000.csv")
DB_PATH = os.path.join(BASE_DIR, "spotify.db")

def create_db():
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    conn = sqlite3.connect(DB_PATH)

    # -------------------------
    # ARTISTS TABLE
    # -------------------------
    artists = df[["artists"]].dropna().drop_duplicates().reset_index(drop=True)
    artists["artist_id"] = range(1, len(artists) + 1)
    artists = artists.rename(columns={"artists": "artist_name"})
    artists.to_sql("artists", conn, if_exists="replace", index=False)

    # -------------------------
    # GENRES TABLE
    # -------------------------
    genres = df[["genre"]].dropna().drop_duplicates().reset_index(drop=True)
    genres["genre_id"] = range(1, len(genres) + 1)
    genres = genres.rename(columns={"genre": "genre_name"})
    genres.to_sql("genres", conn, if_exists="replace", index=False)

    # -------------------------
    # MAP IDS INTO TRACKS
    # -------------------------
    df = df.merge(artists, left_on="artists", right_on="artist_name", how="left")
    df = df.merge(genres, left_on="genre", right_on="genre_name", how="left")

    # -------------------------
    # TRACKS TABLE
    # -------------------------
    tracks = df[[
        "track_name",
        "artist_id",
        "genre_id",
        "popularity",
        "danceability",
        "energy",
        "valence",
        "tempo",
        "duration_ms"
    ]].copy()

    tracks.insert(0, "track_id", range(1, len(tracks) + 1))

    tracks.to_sql("tracks", conn, if_exists="replace", index=False)

    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
