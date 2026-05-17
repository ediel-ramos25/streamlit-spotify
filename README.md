# 🎧 Spotify Analytics Dashboard

Streamlit dashboard built using Spotify dataset stored in SQLite. The project allows users to explore music trends, audio features, artist performance, and genre-based analytics using interactive filters and visualizations.

The dashboard enables analysis of track popularity, energy, danceability, and duration across different genres and artists, providing insights into music characteristics and listening patterns.

---

## 📊 Dataset

- `spotify.csv` — Dataset containing track-level audio features and metadata.

Each record includes:
- track_id
- track_name
- artists
- track_genre
- popularity
- duration_ms
- danceability
- energy
- valence
- tempo
- loudness
- speechiness
- instrumentalness
- liveness

---

## 🗄️ Data loading

* Install dependencies:

```bash
pip install pandas streamlit matplotlib sqlite3