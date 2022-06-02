
# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

"""
OUTLINES
    
NEXT STEPS

"""


import pandas as pd, numpy as np, calendar
import helpdesk as hd
import datetime

DEBUG = True

class Data(object):
    pass

df = Data() 
summ = Data() 


# Adding the racing folder to the PATH variable 
import sys
sys.path.append('C:\\Users\\karan\\Documents\\Code\\racing')
print(sys.path)

# Import libraries
from datetime import datetime
from datetime import timedelta
from dateutil import tz

import math

import numpy as np
import pandas as pd

from scipy.stats import zscore
from sklearn.linear_model import LogisticRegression

import betfairlightweight
from betfairlightweight import filters

import fasttrack as ft

fasttrack_key = "dcc0a791-6b18-4cc4-8d46-453a00e9b7e4"

my_username = "kdsbhatti@gmail.com"
my_password = "B3tf@1rp@ss"
my_app_key = "U9o0IvlKooTsPHsv"


#----------------------------------------------------------------- RETRIEVE FT LISTINGS -----------------------------------------------------------------

greys = ft.Fasttrack(fasttrack_key)
track_codes = greys.listTracks()
print(track_codes.head())

#tracks_filter = list(track_codes[track_codes['state'] == 'QLD']['track_code'])
tracks_filter = list(track_codes['track_code'])
print(tracks_filter)


#race_details, dog_results = greys.getRaceResults('2018-01-01', '2021-06-15', tracks_filter)

#races_today, dogs_today = greys.getBasicFormat('2021-06-02', tracks_filter)
races_today, dogs_today = greys.getFullFormat('2021-06-02', tracks_filter)
print(races_today.head())


# Tracks Today
tracks_today = list(races_today['Track'].unique())
print(tracks_today)



#----------------------------------------------------------------- RETRIEVE BF LISTINGS -----------------------------------------------------------------

#----------------------------------------------------------------- Greyhound Event Filter ---------------------------------------------------------------


trading = betfairlightweight.APIClient(my_username, my_password, app_key=my_app_key)
print(trading.login_interactive())

# Create the market filter
greyhounds_event_filter = filters.market_filter(
        event_type_ids = [4339],
        market_countries = ['AU'],
        market_start_time={'to': (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT%TZ")}
    )



# Get a list of all greyhound events as objects
greyhounds_events = trading.betting.list_events( filter = greyhounds_event_filter )


# Create a DataFrame with all the events by iterating over each event object
greyhounds_events_today = pd.DataFrame({
    'Event Name': [event_object.event.name for event_object in greyhounds_events],
    'Event ID': [event_object.event.id for event_object in greyhounds_events],
    'Event Venue': [event_object.event.venue for event_object in greyhounds_events],
    'Country Code': [event_object.event.country_code for event_object in greyhounds_events],
    'Time Zone': [event_object.event.time_zone for event_object in greyhounds_events],
    'Open Date': [event_object.event.open_date for event_object in greyhounds_events],
    'Market Count': [event_object.market_count for event_object in greyhounds_events]
})


print(greyhounds_events_today.head())

greyhounds_events_today = greyhounds_events_today[greyhounds_events_today['Event Venue'].isin(tracks_today)]

print(greyhounds_events_today.head())

#----------------------------------------------------------------- Greyhound Market Catalogue -----------------------------------------------------------

market_catalogue_filter = filters.market_filter(event_ids = list(greyhounds_events_today['Event ID']),market_type_codes = ['WIN'])


market_catalogue = trading.betting.list_market_catalogue(
    filter=market_catalogue_filter,
    max_results='1000',
    sort='FIRST_TO_START',
    market_projection=['MARKET_START_TIME', 'MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION', 'EVENT', 'EVENT_TYPE']
)

win_markets = []
runners = []


for market_object in market_catalogue:
    # win_markets_df.append({
    #     'Event Name': market_object.event.name,
    #     'Event ID': market_object.event.id,
    #     'Event Venue': market_object.event_venue,
    #     'Market Name': market_object.market_name,
    #     'Market ID': market_object.market_id,
    #     'Market start time': market_object.market_start_time,
    #     'Total Matched': market_object.total_matched
    #     })
    win_markets.append({
        'event_name': market_object.event.name,
        'event_id': market_object.event.id,
        'event_venue': market_object.event.venue,
        'market_name': market_object.market_name,
        'market_id': market_object.market_id,
        'market_start_time': market_object.market_start_time,
        'total_matched': market_object.total_matched
        })

    for runner in market_object.runners:
        runners.append({
            'market_id': market_object.market_id,
            'runner_id': runner.selection_id,
            'runner_name': runner.runner_name
            })

win_markets_df = pd.DataFrame(win_markets)

df.runners_raw = pd.DataFrame(runners)


# Extract race number from market name
win_markets_df['race_number'] = win_markets_df['market_name'].apply(lambda x: x[1:3].strip() if x[0] == 'R' else None)

# Functions that returns the time from a newly specified timezone given a time and an old timezone
def change_timezone(time, oldtz, newtz):
    from_zone = tz.gettz(oldtz)
    to_zone = tz.gettz(newtz)
    newtime = time.replace(tzinfo = from_zone).astimezone(to_zone).replace(tzinfo = None)
    return newtime

# Add in a local_start_time variable
win_markets_df['local_start_time'] = win_markets_df['market_start_time'].apply(lambda x: change_timezone(x, 'UTC', 'Australia/Sydney'))

print(win_markets_df.head())



# Remove dog number from runner_name
df.runners_raw['runner_name'] = df.runners_raw['runner_name'].apply( lambda x: x[(x.find(" ") + 1):].upper() )

# Merge on the race number and event venue onto runners_df
df.runners = pd.merge( df.runners_raw, win_markets_df[['market_id', 'event_venue', 'race_number']], how = 'left', on = 'market_id')

print(df.runners.head())


#----------------------------------------------------------------- MERGE FT & BF DATA -----------------------------------------------------------


races_today = races_today.rename(columns = {'@id': 'FastTrack_RaceId'})
races_today = races_today[['FastTrack_RaceId', 'Date', 'Track', 'RaceNum', 'RaceName', 'RaceTime', 'Distance', 'RaceGrade']]

dogs_today = dogs_today.rename(columns = {'@id': 'FastTrack_DogId', 'RaceId': 'FastTrack_RaceId'})
dogs_today = dogs_today.merge( races_today[['FastTrack_RaceId', 'Track', 'RaceNum']], how = 'left', on = 'FastTrack_RaceId' )
dogs_today['DogName_bf'] = dogs_today['DogName'].apply(lambda x: x.replace("'", "").replace(".", "").replace("Res", "").strip())



print(df.runners.event_venue.unique())
print(dogs_today.Track.unique())

print(df.runners.runner_name.unique())
print(dogs_today.DogName_bf.unique())

bf_dogs = set(df.runners.runner_name.unique())
ft_dogs = set(dogs_today.DogName_bf.unique())

dogs_is = bf_dogs.intersection(ft_dogs)


print(dogs_today.columns.values.tolist())

#dogs_today.RaceNum.unique()

df.runners.columns.values.tolist()

#
#dogs_filt = dogs_today[ (dogs_today.Track.isin(['Albion Park'])) & (dogs_today.DogName_bf.isin(['DULCERIA','FARMOR MILLES'])) ]
dogs_filt_ft = dogs_today[ (dogs_today.Track.isin(['Albion Park'])) & (dogs_today.RaceNum.isin(['2'])) ]

dogs_filt_bf = df.runners[ (df.runners.event_venue.isin(['Albion Park'])) & (df.runners.race_number.isin(['8'])) ]

# Match on the fastTrack dogId to the runners_df
df.runners_main = pd.merge( df.runners,  dogs_today[['DogName_bf', 'Track', 'RaceNum', 'FastTrack_DogId']],
    how = 'left',
    left_on = ['runner_name', 'event_venue', 'race_number'],
    right_on = ['DogName_bf', 'Track', 'RaceNum'],
    ).drop(['DogName_bf', 'Track', 'RaceNum'], axis = 1)

# Check all betfair selections are matched to a fastTrack dogId by checking if there are any null dogIds
df.runners_main['FastTrack_DogId'].isnull().any()

summ.runners_main = hd.describe_df(df.runners_main)





