import csv
import datetime

import streamlit as st
import numpy as np
import pandas as pd

st.title('IMDB Analyse')

@st.cache(suppress_st_warning=True)
def get_titles() -> pd.DataFrame:
    cache_progress = st.progress(0)

    # Basic info for every titles
    basics_file = pd.read_table('title.basics.tsv',
        sep='\t',
        lineterminator='\n',
        quotechar='', # else rows with " in title wont work
        quoting=csv.QUOTE_NONE,
        dtype={
            'tconst': 'string',
            'titleType': 'string',
            'primaryTitle': 'string',
            'originalTitle': 'string',
            'isAdult': 'float',
            'startYear': 'float',
            'endYear': 'float',
            'runtimeMinutes': 'float',
            'genres': 'string'
            },
        na_values=['\\N']
    )
    cache_progress.progress(10)

    # Ratings for all titles
    ratings_file = pd.read_table('title.ratings.tsv',
        sep='\t',
        lineterminator='\n',
        quotechar='', # else rows with " in title wont work
        quoting=csv.QUOTE_NONE,
        dtype={
            'tconst': 'string',
            'averageRating': 'float',
            'numVotes': 'int'
            },
        na_values=['\\N']
    )
    cache_progress.progress(20)

    # Add ratings to basic info
    ratings_merged = pd.merge(basics_file, ratings_file, how='left', on='tconst')
    cache_progress.progress(30)

    # Remove unused memory
    del(basics_file)
    
    # Info for every episode titles and the id for the parent serie title
    episode_file = pd.read_table('title.episode.tsv',
        sep='\t',
        lineterminator='\n',
        quotechar='', # else rows with ' in title wont work
        quoting=csv.QUOTE_NONE,
        dtype={
            'tconst': 'string',
            'parentTconst': 'string',
            'seasonNumber': 'float',
            'episodeNumber': 'float'
            },
        na_values=['\\N']
    )
    cache_progress.progress(40)

    # Add episode info to some titles
    episode_merged = pd.merge(ratings_merged, episode_file, how='left', on='tconst')
    cache_progress.progress(50)

    # Remove unused memory
    del(episode_file)

    # Add parent info
    parent_info = ratings_merged.copy()
    parent_info.rename(columns = {'tconst':'parentTconst'}, inplace = True)
    parent_info.rename(columns = {'titleType':'parentTitleType'}, inplace = True)
    parent_info.rename(columns = {'primaryTitle':'parentPrimaryTitle'}, inplace = True)
    parent_info.rename(columns = {'originalTitle':'parentOriginalTitle'}, inplace = True)
    parent_info.rename(columns = {'isAdult':'parentIsAdult'}, inplace = True)
    parent_info.rename(columns = {'startYear':'parentStartYear'}, inplace = True)
    parent_info.rename(columns = {'endYear':'parentEndYear'}, inplace = True)
    parent_info.rename(columns = {'runtimeMinutes':'parentRuntimeMinutes'}, inplace = True)
    parent_info.rename(columns = {'genres':'parentGenres'}, inplace = True)
    parent_info.rename(columns = {'averageRating':'parentAverageRating'}, inplace = True)
    parent_info.rename(columns = {'numVotes':'parentNumVotes'}, inplace = True)
    cache_progress.progress(60)

    # Remove unused memory
    del(ratings_merged)

    parent_merged = pd.merge(episode_merged, parent_info, how='left', on='parentTconst')
    cache_progress.progress(70)

    # Remove unused memory
    del(episode_merged)
    del(parent_info)

    cache_progress.progress(100)

    return parent_merged

df = get_titles()
st.dataframe(df.head())

st.text(f"Length before filter: {len(df)}")

# filter input
filter_year = st.slider('Minimal year', min_value=1950.0, max_value=2022.0, value=2000.0)
filter_votes = st.slider('Minimal amount of votes', min_value=0.0, max_value=400.0, value=100.0)
filter_ratings = st.slider('Average rating', min_value=0.0, max_value=10.0, value=7.0)
filter_type = st.selectbox('Title type', list(df['titleType'].unique()), index=4)

# apply filters
df = df[(df['startYear'] >= filter_year) & (df['numVotes'] > filter_votes) & (df['averageRating'] > filter_ratings) & (df['isAdult'] == 1.0)]
st.dataframe(df.head())

st.text(f"Length after filter: {len(df)}")

# upcoming releases are np.NaN, but move them to next year
next_year = float(datetime.datetime.now().year+1)
df = df.replace(to_replace={'startYear': np.NaN, 'endYear':  np.NaN}, value=next_year)
st.dataframe(df.head())

df = df.sort_values("averageRating", ascending=False)
st.dataframe(df)