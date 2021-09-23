import pandas as pd
import lzma
import pickle 
import requests
from zipfile import ZipFile
import joblib
from spotify_client import retrieve_audio_features
def explicit_binarizer(x):
    if x == True:
        return 1
    else:
        return 0

def decade_function(x):
    if x in range(1900, 1991):
        return '1900-1990'
    elif x in range(1991, 1996):
        return '1991-1995'
    elif x in range(1996, 2001):
        return '1996-2000'
    elif x in range(2001, 2006):
        return '2001-2005'
    elif x == 2006:
        return '2006'
    elif x == 2007:
        return '2007'
    elif x == 2008:
        return '2008'
    elif x == 2009:
        return '2009'
    elif x == 2010:
        return '2010'
    elif x == 2011:
        return '2011'
    elif x == 2012:
        return '2012'
    elif x == 2013:
        return '2013'
    elif x == 2014:
        return '2014'
    elif x == 2015:
        return '2015'
    elif x == 2016:
        return '2016'
    elif x == 2017:
        return '2017'
    elif x == 2018:
        return '2018'
    elif x == 2019:
        return '2019'
    elif x == 2020:
        return '2020'
    elif x == 2021:
        return '2021'

def wrangle(df):
    #df.drop(columns='Unnamed: 0', inplace=True)
    df['explicit'] = df['explicit'].apply(explicit_binarizer)
    df['age'] = df['year'].apply(decade_function)
    loaded_ohe = joblib.load('ohe.joblib')
    df = loaded_ohe.transform(df.fillna('Missing'))
    # feature scailing for float columns in df3
    loaded_scaler = joblib.load('scaler.joblib')
    scale_cols = ['danceability', 'energy', 'loudness', 'speechiness',
                  'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                  'time_signature', 'key', 'mode']
    scaled = df[scale_cols].reset_index(drop=True)
    scaler = loaded_scaler
    scaled_float_df = pd.DataFrame(
        scaler.transform(scaled), columns=scaled.columns)
    df.drop(columns=scale_cols, inplace=True)
    df = pd.concat([df, scaled_float_df], axis=1)
    df.drop(columns='year', inplace=True)
    return df

def song_recommender(features):
        desired_keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'year', 'explicit', 'time_signature']
        features_keys = [x for x in features[0].keys() if x in desired_keys] + ['year', 'explicit']
        features_values = [y for x, y in features[0].items()if x in desired_keys] + ['', 0]
        # create dataframe with the f
 
        features_tracks_df = pd.DataFrame(
            data=[features_values], columns=features_keys)
        wrangled_features_tracks_df = wrangle(features_tracks_df)
        # Load pickled model and recommendations lookup dataframe
        knn_loader = joblib.load('knn_model.joblib')
        
        # Load unwrangled dataset to match the song.
        with ZipFile('df_rec_lookup.zip', 'r') as zip:
            zip.extractall()
        df_rec_lookup = pd.read_csv('df_rec_lookup.csv')

        # Query Using kneighbors
        __, neigh_index = knn_loader.kneighbors(wrangled_features_tracks_df)

        # Instantiate song list
        song_list = []
        for i in neigh_index[0][:5]:
            song_list.append(df_rec_lookup['id'][i])
        return song_list

    