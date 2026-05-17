# ======================================================
# create_db.py
# ======================================================

import pandas as pd
import sqlite3
import kagglehub
from kagglehub import KaggleDatasetAdapter


# ======================================================
# DOWNLOAD DATASET FROM KAGGLE
# ======================================================

print("Downloading Spotify dataset...")

df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "maharshipandya/-spotify-tracks-dataset",
    "dataset.csv"
)

print("Dataset loaded successfully.")


# ======================================================
# CLEAN DATA
# ======================================================

# Split artists by ";"
df = df.assign(
    artist=df["artists"].str.split(";")
).explode("artist")

# Remove extra spaces
df["artist"] = df["artist"].str.strip()


# ======================================================
# CREATE SQLITE DATABASE
# ======================================================

conn = sqlite3.connect("spotify.db")

print("Database connection established.")


# ======================================================
# CREATE ARTISTS TABLE
# ======================================================

artists_df = (
    df[["artist"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

artists_df["artist_id"] = artists_df.index + 1

artists_df = artists_df[[
    "artist_id",
    "artist"
]]

artists_df.to_sql(
    "artists",
    conn,
    if_exists="replace",
    index=False
)

print("artists table created.")


# ======================================================
# CREATE GENRES TABLE
# ======================================================

genres_df = (
    df[["track_genre"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

genres_df["genre_id"] = genres_df.index + 1

genres_df = genres_df.rename(
    columns={"track_genre": "genre_name"}
)

genres_df = genres_df[[
    "genre_id",
    "genre_name"
]]

genres_df.to_sql(
    "genres",
    conn,
    if_exists="replace",
    index=False
)

print("genres table created.")


# ======================================================
# MERGE IDS
# ======================================================

df = df.merge(
    artists_df,
    on="artist",
    how="left"
)

df = df.merge(
    genres_df,
    left_on="track_genre",
    right_on="genre_name",
    how="left"
)


# ======================================================
# CREATE TRACKS TABLE
# ======================================================

tracks_df = df[[
    "track_id",
    "track_name",
    "artist_id",
    "genre_id",
    "popularity",
    "duration_ms",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature"
]]

tracks_df.to_sql(
    "tracks",
    conn,
    if_exists="replace",
    index=False
)

print("tracks table created.")


# ======================================================
# VERIFY TABLES
# ======================================================

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM tracks")
tracks_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM artists")
artists_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM genres")
genres_count = cursor.fetchone()[0]

print("\n========== DATABASE SUMMARY ==========")
print(f"Tracks: {tracks_count}")
print(f"Artists: {artists_count}")
print(f"Genres: {genres_count}")


# ======================================================
# CLOSE CONNECTION
# ======================================================

conn.close()

print("\nDatabase successfully created.")
