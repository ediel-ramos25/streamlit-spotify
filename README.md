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
## Installing spotify.csv

- Go to https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset
- Download the .csv file as spotify.csv

## 🗄️ Data loading

* Install dependencies:

```bash
pip install pandas streamlit matplotlib sqlite3
