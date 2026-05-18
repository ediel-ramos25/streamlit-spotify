import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "spotify_50000.csv")
DB_PATH = os.path.join(BASE_DIR, "spotify.db")

# Load CSV
df = pd.read_csv(CSV_PATH)

# Connect DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clean column names (IMPORTANT)
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Drop old tables (rebuild clean)
cursor.execute("DROP TABLE IF EXISTS tracks")

# Create main table (adjusted to typical Spotify dataset)
cursor.execute("""
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_name TEXT,
    artist TEXT,
    genre TEXT,
    popularity INTEGER,
    danceability REAL,
    energy REAL,
    valence REAL,
    tempo REAL,
    duration_ms INTEGER
)
""")

# Insert data safely
df.to_sql("tracks", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Database created successfully at spotify.db")
