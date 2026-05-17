# =========================================================
# IMPORTAR LIBRERÍAS
# =========================================================

import pandas as pd
import sqlite3


# =========================================================
# LEER EL ARCHIVO CSV
# =========================================================

# Cargar el dataset de Spotify
df = pd.read_csv("data/spotify.csv")

print("EXITO: CSV cargado correctamente.")

df = df.assign(artist=df["artists"].str.split(";")).explode("artist")
# =========================================================
# CREAR / CONECTAR A LA BASE DE DATOS
# =========================================================

# Crear el archivo spotify.db
conn = sqlite3.connect("spotify.db")

print("EXITO: Base de datos creada y conexión establecida.")


# =========================================================
# CREAR TABLA DE ARTISTAS
# =========================================================

# Obtener artistas únicos

artists_df = (
    df.assign(artist=df["artists"].str.split(";"))
      .explode("artist")[["artist"]]
      .drop_duplicates()
      .reset_index(drop=True)
)

# Crear un artist_id automático
artists_df["artist_id"] = artists_df.index + 1

# Reordenar columnas
artists_df = artists_df[["artist_id", "artist"]]

# Guardar tabla en SQLite
artists_df.to_sql(
    "artists",
    conn,
    if_exists="replace",
    index=False
)

print("EXITO: Tabla artists creada.")


# =========================================================
# CREAR TABLA DE GÉNEROS
# =========================================================

# Obtener géneros únicos
genres_df = df[["track_genre"]].drop_duplicates().reset_index(drop=True)

# Crear genre_id automático
genres_df["genre_id"] = genres_df.index + 1

# Renombrar columna
genres_df = genres_df.rename(
    columns={"track_genre": "genre_name"}
)

# Reordenar columnas
genres_df = genres_df[["genre_id", "genre_name"]]

# Guardar tabla en SQLite
genres_df.to_sql(
    "genres",
    conn,
    if_exists="replace",
    index=False
)

print("EXITO: Tabla genres creada.")


# =========================================================
# AGREGAR artist_id AL DATAFRAME ORIGINAL
# =========================================================

# Hacer merge para obtener artist_id
df = df.merge(
    artists_df,
    on="artist",
    how="left"
)


# =========================================================
# AGREGAR genre_id AL DATAFRAME ORIGINAL
# =========================================================

# Hacer merge para obtener genre_id
df = df.merge(
    genres_df,
    left_on="track_genre",
    right_on="genre_name",
    how="left"
)


# =========================================================
# CREAR TABLA TRACKS
# =========================================================

# Seleccionar columnas importantes
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

# Guardar tabla tracks
tracks_df.to_sql(
    "tracks",
    conn,
    if_exists="replace",
    index=False
)

print("EXITO: Tabla tracks creada.")


# =========================================================
# VERIFICAR CANTIDAD DE REGISTROS
# =========================================================

cursor = conn.cursor()

# Contar tracks
cursor.execute("SELECT COUNT(*) FROM tracks")
tracks_count = cursor.fetchone()[0]

# Contar artistas
cursor.execute("SELECT COUNT(*) FROM artists")
artists_count = cursor.fetchone()[0]

# Contar géneros
cursor.execute("SELECT COUNT(*) FROM genres")
genres_count = cursor.fetchone()[0]

print("\n========== RESUMEN ==========")
print(f"Tracks: {tracks_count}")
print(f"Artists: {artists_count}")
print(f"Genres: {genres_count}")


# =========================================================
# CERRAR CONEXIÓN
# =========================================================

conn.close()

print("\nEXITO: Datos insertados y conexión cerrada.")