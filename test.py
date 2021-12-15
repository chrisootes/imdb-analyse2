import csv

import pandas as pd

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

print(basics_file)