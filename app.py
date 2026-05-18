# ======================================================
# IMPORTAR LIBRERÍAS
# ======================================================
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# ======================================================
# CONFIGURACIÓN GENERAL DE STREAMLIT
# ======================================================
st.set_page_config(
    page_title="Spotify Analytics Dashboard",
    layout="wide"
)

st.title("🎧 Spotify Analytics Dashboard")
st.markdown("Análisis de música con SQLite + Streamlit")

# ======================================================
# RUTAS SEGURAS (IMPORTANTE PARA STREAMLIT CLOUD)
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spotify.db")
CSV_PATH = os.path.join(BASE_DIR, "spotify_50000.csv")

# ======================================================
# CREAR / CARGAR BASE DE DATOS SI NO EXISTE
# ======================================================
@st.cache_resource
def init_db():
    """
    Crea la base de datos desde CSV si no existe.
    Esto evita errores en Streamlit Cloud.
    """
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_csv(CSV_PATH)

    # Limpieza de nombres de columnas
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Guardar en SQLite
    df.to_sql("tracks", conn, if_exists="replace", index=False)

    conn.close()

init_db()

# ======================================================
# CONEXIÓN A SQLITE (CACHEADA)
# ======================================================
@st.cache_resource
def get_connection():
    """Mantiene una conexión reutilizable a SQLite"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# ======================================================
# FUNCIÓN DE QUERY CACHEADA
# ======================================================
@st.cache_data(ttl=3600)
def cached_query(query, params=None):
    """
    Ejecuta queries SQL con cache para mejorar rendimiento.
    ttl=3600 → se actualiza cada 1 hora
    """
    if params is None:
        params = ()

    return pd.read_sql_query(query, conn, params=params)

# ======================================================
# CARGA DE DATOS BÁSICOS (FILTROS)
# ======================================================
def load_genres():
    """
    Obtiene lista de géneros únicos desde el dataset.
    """
    query = """
    SELECT DISTINCT genre
    FROM tracks
    ORDER BY genre
    """
    return cached_query(query)

# ======================================================
# QUERY PRINCIPAL CON FILTROS
# ======================================================
def get_filtered_tracks(selected_genre, search_text, popularity_min):
    """
    Devuelve canciones filtradas según:
    - género
    - búsqueda por nombre
    - popularidad mínima
    """

    query = """
    SELECT *
    FROM tracks
    WHERE popularity >= ?
    AND track_name LIKE ?
    """

    params = [popularity_min, f"%{search_text}%"]

    # Filtro por género (si no es "Todos")
    if selected_genre != "Todos":
        query += " AND genre = ?"
        params.append(selected_genre)

    query += " ORDER BY popularity DESC"

    return cached_query(query, tuple(params))

# ======================================================
# TOP ARTISTAS
# ======================================================
def top_artists_query():
    """
    Calcula artistas más populares.
    """
    query = """
    SELECT
        artist,
        AVG(popularity) AS avg_popularity,
        COUNT(*) AS total_tracks
    FROM tracks
    GROUP BY artist
    HAVING COUNT(*) >= 5
    ORDER BY avg_popularity DESC
    LIMIT 10
    """

    return cached_query(query)

# ======================================================
# DURACIÓN POR GÉNERO
# ======================================================
def duration_by_genre_query():
    """
    Duración promedio por género en minutos
    """
    query = """
    SELECT
        genre,
        AVG(duration_ms) / 60000.0 AS avg_minutes
    FROM tracks
    GROUP BY genre
    ORDER BY avg_minutes DESC
    LIMIT 15
    """

    return cached_query(query)

# ======================================================
# SIDEBAR - FILTROS
# ======================================================
st.sidebar.header("Filtros")

genres_df = load_genres()

genre_list = ["Todos"] + genres_df["genre"].dropna().tolist()

selected_genre = st.sidebar.selectbox("Género", genre_list)

search_text = st.sidebar.text_input("Buscar canción")

popularity_min = st.sidebar.slider("Popularidad mínima", 0, 100, 50)

# ======================================================
# DATA FILTRADA
# ======================================================
filtered_tracks = get_filtered_tracks(
    selected_genre,
    search_text,
    popularity_min
)

# ======================================================
# MÉTRICAS PRINCIPALES
# ======================================================
st.subheader("Resumen")

col1, col2, col3 = st.columns(3)

col1.metric("Canciones", len(filtered_tracks))

col2.metric(
    "Popularidad promedio",
    round(filtered_tracks["popularity"].mean(), 2)
    if not filtered_tracks.empty else 0
)

col3.metric(
    "Energía promedio",
    round(filtered_tracks["energy"].mean(), 2)
    if not filtered_tracks.empty else 0
)

# ======================================================
# PREVIEW DE DATOS
# ======================================================
st.subheader("Datos filtrados")
st.dataframe(filtered_tracks.head(50))

# ======================================================
# GRÁFICO: ENERGY vs DANCEABILITY
# ======================================================
st.subheader("Energy vs Danceability")

fig1, ax1 = plt.subplots()

if not filtered_tracks.empty:
    ax1.scatter(
        filtered_tracks["energy"],
        filtered_tracks["danceability"]
    )

ax1.set_xlabel("Energy")
ax1.set_ylabel("Danceability")

st.pyplot(fig1)

# ======================================================
# TOP ARTISTAS
# ======================================================
st.subheader("Top 10 artistas")

artists_df = top_artists_query()

fig2, ax2 = plt.subplots()

ax2.bar(
    artists_df["artist"],
    artists_df["avg_popularity"]
)

ax2.set_xlabel("Artista")
ax2.set_ylabel("Popularidad promedio")

plt.xticks(rotation=45)

st.pyplot(fig2)

# ======================================================
# DURACIÓN POR GÉNERO
# ======================================================
st.subheader("⏱ Duración promedio por género")

length_df = duration_by_genre_query()

fig3, ax3 = plt.subplots()

ax3.bar(
    length_df["genre"],
    length_df["avg_minutes"]
)

ax3.set_xlabel("Género")
ax3.set_ylabel("Minutos")

plt.xticks(rotation=30)

st.pyplot(fig3)

# ======================================================
# CIERRE DE CONEXIÓN
# ======================================================
conn.close()
