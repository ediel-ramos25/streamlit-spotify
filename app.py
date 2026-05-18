import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# ----------------------------
# PATH FIX (VERY IMPORTANT)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spotify.db")

# ----------------------------
# DB CONNECTION
# ----------------------------
def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ----------------------------
# LOAD DATA
# ----------------------------
def load_tracks():
    query = "SELECT * FROM tracks"
    return get_data(query)

df = load_tracks()

# ----------------------------
# UI
# ----------------------------
st.title("Spotify Dashboard")

st.sidebar.header("Filters")

# Genre filter (safe fallback)
if "genre" in df.columns:
    genres = df["genre"].dropna().unique()
    selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + list(genres))
else:
    selected_genre = "All"

# Filter dataset
filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

# ----------------------------
# KPIs
# ----------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Tracks", len(filtered_df))
col2.metric("Avg Popularity", round(filtered_df["popularity"].mean(), 2))
col3.metric("Avg Tempo", round(filtered_df["tempo"].mean(), 2))

# ----------------------------
# Charts
# ----------------------------
st.subheader("Popularity Distribution")

fig1 = px.histogram(filtered_df, x="popularity")
st.plotly_chart(fig1)

st.subheader("Energy vs Danceability")

fig2 = px.scatter(
    filtered_df,
    x="energy",
    y="danceability",
    color="popularity"
)

st.plotly_chart(fig2)

# ----------------------------
# DATA TABLE
# ----------------------------
st.subheader("Raw Data")
st.dataframe(filtered_df)
