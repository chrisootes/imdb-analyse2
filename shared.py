import csv
import datetime

import streamlit as st
import numpy as np
import pandas as pd

@st.cache_data
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

    # upcoming releases are np.NaN, but move them to next year
    next_year = float(datetime.datetime.now().year+1)
    parent_merged.replace(to_replace={'startYear': np.NaN, 'endYear':  np.NaN}, value=next_year, inplace=True)
    #st.dataframe(parent_merged.head())

    cache_progress.progress(100)

    return parent_merged


@st.cache_data
def spread_episode_year(episodes):
    spread_progress = st.progress(0.0)
    # Sort episodes
    episodes = episodes.sort_values(by=["parentTconst", "startYear", "seasonNumber", "episodeNumber"])
    # Reset index
    episodes = episodes.reset_index()
    episodes.pop("index")
    #st.dataframe(episodes.head())
    episodes_in_year = episodes.groupby(['parentTconst','startYear']).size().reset_index().rename(columns={0:'count'})
    #st.dataframe(episodes_in_year.head())
    # add columns begin and end day in year
    episodes["episodes_start"] = 0.0
    episodes["episodes_end"] = 0.0
    # because of sort count episodes
    last_start_number = 0.0
    last_parentTconst = ""
    last_startYear = ""
    last_seasonNumber = 0.0
    # loop
    episodes_len = len(episodes)
    for i in range(episodes_len):
        spread_progress.progress((i+1.0)/episodes_len)
        row = episodes.loc[i]
        current_episodes_in_year = episodes_in_year[(episodes_in_year["parentTconst"] == row["parentTconst"]) & (episodes_in_year["startYear"] == row["startYear"])]
        if len(current_episodes_in_year) != 1:
            st.error(current_episodes_in_year)
            st.dataframe(row)
            break
        current_episodes_in_year = current_episodes_in_year["count"].iloc[0]
        distributed = 1.0/current_episodes_in_year
        if last_parentTconst != row["parentTconst"]:
            last_start_number = 0.0
            last_parentTconst = row["parentTconst"]
        if last_startYear != row["startYear"]:
            last_start_number = 0.0
            last_startYear = row["startYear"]
        episodes.loc[i, "episodes_start"] = row["startYear"]+distributed*last_start_number
        episodes.loc[i, "episodes_end"] = row["startYear"]+distributed*(last_start_number+1.0)
        last_start_number += 1.0
    return episodes

@st.cache_data
def spread_movie_year(movies: pd.DataFrame):
    spread_progress = st.progress(0.0)
    # Sort
    movies.sort_values(by=["startYear"], inplace=True)
    #st.dataframe(movies.head())
    # Reset index
    movies = movies.reset_index()
    movies.pop("index")
    movies["parentPrimaryTitle"] = movies["primaryTitle"]
    #st.dataframe(movies.head())
    # add columns begin and end day in year
    movies["episodes_start"] = movies["startYear"]
    movies["episodes_end"] = movies["startYear"]+1.0
    return movies