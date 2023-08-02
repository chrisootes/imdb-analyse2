import csv
import datetime

import streamlit as st
import numpy as np
import pandas as pd

import shared

st.title('IMDB Adult Analyse')

df = shared.get_titles()
st.dataframe(df.head())

st.text(f"Length before filter: {len(df)}")

# filter input
filter_year = st.slider('Minimal year', min_value=1950.0, max_value=2022.0, value=2000.0)
filter_votes = st.slider('Minimal amount of votes', min_value=0.0, max_value=400.0, value=100.0)
filter_ratings = st.slider('Average rating', min_value=0.0, max_value=10.0, value=7.0)
filter_type = st.selectbox('Title type', list(df['titleType'].unique()), index=4)

# apply filters
df_filtered = df[(df['startYear'] >= filter_year) & (df['numVotes'] > filter_votes) & (df['averageRating'] > filter_ratings) & (df['isAdult'] == 1.0)]
st.dataframe(df_filtered.head())

st.text(f"Length after filter: {len(df_filtered)}")

df_sorted = df_filtered.sort_values("averageRating", ascending=False)
st.dataframe(df_sorted)