import csv
import datetime

import streamlit as st
import numpy as np
import pandas as pd

import shared

st.set_page_config(
   page_title="IMDB Analyse",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)
st.title('IMDB Analyse')

df = shared.get_titles()
st.dataframe(df.head())

st.text(f"Length before filter: {len(df)}")

# filter input
filter_parents = st.checkbox('Apply on parents')
filter_adult = st.checkbox('Adult')
filter_year = st.slider('Minimal year', min_value=1950.0, max_value=2050.0, value=2018.0)
filter_votes = st.slider('Minimal amount of votes', min_value=0.0, max_value=100000.0, value=20000.0)
filter_ratings = st.slider('Average rating', min_value=0.0, max_value=10.0, value=7.0)
#filter_type = st.selectbox('Title type', list(df['titleType'].unique()), index=4)
unique_genres = pd.Series(df['genres'].unique())
unique_genres = unique_genres[unique_genres.str.contains(',') == False]
filter_genres = st.text_input(f'Genres: {list(unique_genres)}', '')
unique_types = df['titleType'].unique()
filter_type = st.text_input(f'Type: {list(unique_types)}', 'tvEpisode')

# apply filters
if filter_parents:
    df_filtered = df[
        (df['parentStartYear'] >= filter_year)
        & (df['parentNumVotes'] > filter_votes)
        & (df['parentAverageRating'] > filter_ratings)
        & (df['parentGenres'].str.contains(filter_genres))
        & (df['parentIsAdult'] == float(filter_adult))
        & (df['titleType'].str.contains(filter_type))
    ]
    df_final = shared.spread_episode_year(df_filtered)
else:
    df_filtered = df[
        (df['startYear'] >= filter_year)
        & (df['numVotes'] > filter_votes)
        & (df['averageRating'] > filter_ratings)
        & (df['genres'].str.contains(filter_genres))
        & (df['isAdult'] == float(filter_adult))
        & (df['titleType'].str.contains(filter_type))
    ]
    df_final = shared.spread_movie_year(df_filtered)

#st.dataframe(df_filtered.head())
st.text(f"Length after filter: {len(df_final)}")
#st.dataframe(df_final.head())

st.vega_lite_chart(
    data=df_final,
    spec={
        'description': 'A simple bar chart with ranged data (aka Gantt Chart).',
        'mark': {
            'type': 'bar',
            'tooltip': True
        },
        'encoding': {
            'x': {
                'field': 'episodes_start',
                'type': 'quantitative',
                "scale": {"domain": [filter_year, float(datetime.datetime.now().year+1)]}
            },
            'x2': {
                'field': 'episodes_end',
                'type': 'quantitative'
            },
            'y': {
                'field': 'parentPrimaryTitle',
                'type': 'nominal',
                'sort': {'field': 'startYear'}
            },
            'color': {
                'field': 'averageRating',
                'type': 'quantitative',
                'scale': {'scheme': 'turbo'}
            },
            "tooltip": [
                {"field": "parentPrimaryTitle", "type": "nominal"},
                {"field": "parentTconst", "type": "nominal"},
                {"field": "startYear", "type": "nominal"},
                {"field": "isAdult", "type": "nominal"},
                {"field": "genres", "type": "nominal"},
                {"field": "averageRating", "type": "nominal"},
                {"field": "numVotes", "type": "nominal"},
                {"field": "seasonNumber", "type": "nominal"},
                {"field": "episodeNumber", "type": "nominal"},
                {"field": "tconst", "type": "nominal"},
            ]
        },
    },
    use_container_width=True
)

if len(df_final) < 1000:
    st.dataframe(df_final)