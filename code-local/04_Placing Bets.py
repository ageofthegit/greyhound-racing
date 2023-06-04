
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


DEBUG = False


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

#----------------------------------------------------------------- ENVIRONMENT VARIABLES FOR ACCESS -----------------------------------------------------------------

import os

#FUTURES_API_KEY = os.environ.get('FUTURES_API_KEY')
FASTTRACK_KEY = os.environ.get('FASTTRACK_KEY')

BETFAIR_USERNAME = os.environ.get('BETFAIR_USERNAME')
BETFAIR_PASSWORD = os.environ.get('BETFAIR_PASSWORD')
BETFAIR_APP_KEY = os.environ.get('BETFAIR_APP_KEY')


#----------------------------------------------------------------- HELPFUL FUNCTIONS -----------------------------------------------------------------

# Functions that returns the time from a newly specified timezone given a time and an old timezone
def change_timezone(time, oldtz, newtz):
    from_zone = tz.gettz(oldtz)
    to_zone = tz.gettz(newtz)
    newtime = time.replace(tzinfo = from_zone).astimezone(to_zone).replace(tzinfo = None)
    return newtime

def roundUpOdds(odds):
    if odds < 2:
        return math.ceil(odds * 100) / 100
    elif odds < 3:
        return math.ceil(odds * 50) / 50
    elif odds < 4:
        return math.ceil(odds * 20) / 20
    elif odds < 6:
        return math.ceil(odds * 10) / 10
    elif odds < 10:
        return math.ceil(odds * 5) / 5
    elif odds < 20:
        return math.ceil(odds * 2) / 2
    elif odds < 30:
        return math.ceil(odds * 1) / 1
    elif odds < 50:
        return math.ceil(odds * 0.5) / 0.5
    elif odds < 100:
        return math.ceil(odds * 0.2) / 0.2
    elif odds < 1000:
        return math.ceil(odds * 0.1) / 0.1
    else:
        return odds


# Create a function to place a bet using betfairlightweight
def placeBackBet(instance, market_id, selection_id, size, price):
    order_filter = filters.limit_order(
        size = size,
        price = price,
        persistence_type = "LAPSE"
    )
    instructions_filter = filters.place_instruction(
        selection_id = str(selection_id),
        order_type = "LIMIT",
        side = "BACK",
        limit_order = order_filter
    )
    order  = instance.betting.place_orders(
        market_id = market_id,
        instructions = [instructions_filter]
    )
    print("Bet Place on selection {0} is {1}".format(str(selection_id), order.__dict__['_data']['status']))
    return order

#----------------------------------------------------------------- RETRIEVE FT LISTINGS -----------------------------------------------------------------

greys = ft.Fasttrack(FASTTRACK_KEY)
track_codes = greys.listTracks()
if DEBUG : print(track_codes.head())

#tracks_filter = list(track_codes[track_codes['state'] == 'QLD']['track_code'])
tracks_filter = list(track_codes['track_code'])
if DEBUG : print(tracks_filter)

#race_details, dog_results = greys.getRaceResults('2022-01-01', '2021-06-15', tracks_filter)

#races_today, dogs_today = greys.getBasicFormat('2022-06-02', tracks_filter)
df.ft_races_today, df.ft_dogs_today = greys.getFullFormat('2022-06-06', tracks_filter)
if DEBUG : print(df.ft_races_today.head())

# Tracks Today
ft_tracks_today = list(df.ft_races_today['Track'].unique())
if DEBUG : print(ft_tracks_today)


df.ft_dogs_today.loc[:,"NumOdds"] = df.ft_dogs_today.apply(lambda x : None if pd.isna(x.Odds) else x['Odds'].replace('$','') , axis = 1)
df.ft_dogs_today["NumOdds"] = df.ft_dogs_today["NumOdds"].astype(float)



df.ft_races_today = df.ft_races_today.rename(columns = {'@id': 'FastTrack_RaceId'})
df.ft_races_today = df.ft_races_today[['FastTrack_RaceId', 'Date', 'Track', 'RaceNum', 'RaceName', 'RaceTime', 'Distance', 'RaceGrade']]

df.ft_dogs_today = df.ft_dogs_today.rename(columns = {'@id': 'FastTrack_DogId', 'RaceId': 'FastTrack_RaceId'})

summ.ft_races_today = hd.describe_df(df.ft_races_today)
summ.ft_dogs_today = hd.describe_df(df.ft_dogs_today.drop(columns = ['Form']))

df.ft_today = pd.merge(df.ft_dogs_today\
                       , df.ft_races_today[['FastTrack_RaceId', 'Track', 'RaceNum']]\
                           , how = 'left'\
                               , on = 'FastTrack_RaceId' )


df.ft_today['DogName_bf'] = df.ft_today['DogName'].apply(lambda x: x.replace("'", "").replace(".", "").replace("Res", "").strip())

summ.ft_today = hd.describe_df(df.ft_today)

#----------------------------------------------------------------- RETRIEVE BF LISTINGS -----------------------------------------------------------------

#----------------------------------------------------------------- Greyhound Event Filter ---------------------------------------------------------------


betfair_api = betfairlightweight.APIClient( BETFAIR_USERNAME, BETFAIR_PASSWORD, app_key= BETFAIR_APP_KEY )
if DEBUG : print(betfair_api.login_interactive())

# Create the market filter
greyhounds_event_filter = filters.market_filter(
        event_type_ids = [4339],
        market_countries = ['AU'],
        market_start_time={'to': (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT%TZ")}
    )


# Get a list of all greyhound events as objects
greyhounds_events = betfair_api.betting.list_events( filter = greyhounds_event_filter )


# Create a DataFrame with all the events by iterating over each event object
df.bf_greyhounds_events_today = pd.DataFrame({
    'Event Name': [event_object.event.name for event_object in greyhounds_events],
    'Event ID': [event_object.event.id for event_object in greyhounds_events],
    'Event Venue': [event_object.event.venue for event_object in greyhounds_events],
    'Country Code': [event_object.event.country_code for event_object in greyhounds_events],
    'Time Zone': [event_object.event.time_zone for event_object in greyhounds_events],
    'Open Date': [event_object.event.open_date for event_object in greyhounds_events],
    'Market Count': [event_object.market_count for event_object in greyhounds_events]
})


if DEBUG : print(df.bf_greyhounds_events_today.head())

df.bf_greyhounds_events_today = df.bf_greyhounds_events_today[df.bf_greyhounds_events_today['Event Venue'].isin(ft_tracks_today)]

if DEBUG : print(df.bf_greyhounds_events_today.head())


#----------------------------------------------------------------- Greyhound Market Catalogue -----------------------------------------------------------

market_catalogue_filter_win = filters.market_filter(event_ids = list(df.bf_greyhounds_events_today['Event ID']),market_type_codes = ['WIN'])
market_catalogue_filter_plc = filters.market_filter(event_ids = list(df.bf_greyhounds_events_today['Event ID']),market_type_codes = ['PLC'])


market_catalogue_win = betfair_api.betting.list_market_catalogue(
    filter=market_catalogue_filter_win,
    max_results='1000',
    sort='FIRST_TO_START',
    market_projection=['MARKET_START_TIME', 'MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION', 'EVENT', 'EVENT_TYPE']
)


market_catalogue_plc = betfair_api.betting.list_market_catalogue(
    filter=market_catalogue_filter_plc,
    max_results='1000',
    sort='FIRST_TO_START',
    market_projection=['MARKET_START_TIME', 'MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION', 'EVENT', 'EVENT_TYPE']
)


win_markets = []
runners = []


for market_object in market_catalogue_win:
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

df.bf_markets_win = pd.DataFrame(win_markets)
df.bf_runners_raw = pd.DataFrame(runners)


# Extract race number from market name
df.bf_markets_win['race_number'] = df.bf_markets_win['market_name'].apply(lambda x: x[1:3].strip() if x[0] == 'R' else None)

# Add in a local_start_time variable
df.bf_markets_win['local_start_time'] = df.bf_markets_win['market_start_time'].apply(lambda x: change_timezone(x, 'UTC', 'Australia/Sydney'))

if DEBUG : print(df.bf_markets_win.head())

# Remove dog number from runner_name
df.bf_runners_raw['runner_name'] = df.bf_runners_raw['runner_name'].apply( lambda x: x[(x.find(" ") + 1):].upper() )

summ.bf_markets_win = hd.describe_df( df.bf_markets_win )
summ.bf_runners_raw = hd.describe_df( df.bf_runners_raw )

# Merge on the race number and event venue onto runners_df
df.bf_today = pd.merge( df.bf_runners_raw\
                       , df.bf_markets_win[['market_id', 'event_venue', 'race_number', 'local_start_time']]\
                           , how = 'left'\
                               , on = 'market_id')

if DEBUG : print(df.bf_today.head())


summ.bf_today = hd.describe_df( df.bf_today)

#----------------------------------------------------------------- MERGE FT & BF DATA -----------------------------------------------------------


print(df.bf_today.shape)
# 532
print(len(df.bf_today.event_venue.unique()))

print(df.ft_today.shape)
# 1142


# Check to see how many Track Merge

bf_tracks = set(df.bf_today.event_venue.unique())
print(len(bf_tracks))
ft_tracks = set(df.ft_today.Track.unique())
print(len(ft_tracks))

tracks_is = bf_tracks.intersection(ft_tracks)
print(len(tracks_is))

# Match on the fastTrack dogId to the runners_df
df.main = pd.merge( df.bf_today\
                   ,  df.ft_today[['DogName_bf', 'Track', 'RaceNum', 'NumOdds', 'FastTrack_DogId', 'DogHandicap']],\
                       how = 'left',\
                           left_on = ['runner_name', 'event_venue', 'race_number'],\
                               right_on = ['DogName_bf', 'Track', 'RaceNum'],\
                                   )


print(df.main.shape)
# 532
print(len(df.main.event_venue.unique()))
# 9
print(len(df.main.market_id.unique()))
# 75
    
# Check all betfair selections are matched to a fastTrack dogId by checking if there are any null dogIds
df.main['FastTrack_DogId'].isnull().any()

summ.main = hd.describe_df(df.main)



#----------------------------------------------------------------- ALGO APPLY -----------------------------------------------------------

#----------------------------------------------------------------- Odds Check -----------------------------------------------------------

grouping = ['Track']
df.main_miss_track = df.main.groupby( grouping )['NumOdds'].apply(lambda x: x.isnull().sum()).reset_index().rename( columns = {'NumOdds':'MissingOdds'} )

grouping = ['market_id']
df.main_miss_marketid = df.main.groupby( grouping )['NumOdds'].apply(lambda x: x.isnull().sum()).reset_index().rename( columns = {'NumOdds':'MissingOdds'} )

grouping = ['Track', 'market_id']
df.main_miss_3 = df.main.groupby( grouping )['NumOdds'].apply(lambda x: x.isnull().sum()).reset_index().rename( columns = {'NumOdds':'MissingOdds'} )

'''

Odds Data Available for 3 / 9 Tracks 
    Shepparton, Traralgon, Ballarat
    


'''

print(len(df.main_miss_marketid[df.main_miss_marketid.MissingOdds == 0].market_id.unique().tolist()))
markets_w_odds = df.main_miss_marketid[df.main_miss_marketid.MissingOdds == 0].market_id.unique().tolist()

df.algodata = df.main[df.main.market_id.isin(markets_w_odds)]

print(df.algodata.shape)
#131

print(df.algodata.event_venue.unique().tolist())
# ['Ballarat', 'Traralgon', 'Shepparton']

print(len(df.algodata.market_id.unique().tolist()))
# 18 Win Markets

#----------------------------------------------------------------- Variable Creation -----------------------------------------------------------

df.algodata.loc[:,"ExpPos"] = df.algodata.groupby( ['market_id'] )['NumOdds'].rank("dense", ascending=True)

df.algodata.loc[:,'flag_expfav'] = df.algodata.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos <= 1 else False, axis = 1)
df.algodata["flag_expfav"] = df.algodata["flag_expfav"].astype(bool)


summ.algodata = hd.describe_df(df.algodata)

#----------------------------------------------------------------- PLACE BETS -----------------------------------------------------------

df.win_data = df.algodata[df.algodata.flag_expfav]

print(df.win_data.shape)
# 18

print(len(df.win_data.event_venue.unique().tolist()))
# 3

print(len(df.win_data.market_id.unique().tolist()))
# 18


market_id = df.win_data['market_id'].values[-1]

df.bets = df.win_data[df.win_data['market_id'] == market_id].reset_index(drop = True)
df.bets['min_odds'] = df.bets['NumOdds'].apply(lambda x: roundUpOdds(x))

summ.bets = hd.describe_df(df.bets)


for selection_id, min_odds in zip(df.bets['runner_id'], df.bets['min_odds']):
    placeBackBet(betfair_api, market_id, selection_id, 5, min_odds)

#----------------------------------------------------------------- MISC CODE -----------------------------------------------------------

# QUALITY CHECK THE MERGE 
print(df.runners.event_venue.unique())
print(df.dogs_today.Track.unique())

print(df.runners.runner_name.unique())
print(df.dogs_today.DogName_bf.unique())

bf_dogs = set(df.runners.runner_name.unique())
ft_dogs = set(df.dogs_today.DogName_bf.unique())

dogs_is = bf_dogs.intersection(ft_dogs)


print(df.dogs_today.columns.values.tolist())
#dogs_today.RaceNum.unique()
print(df.runners.columns.values.tolist())

#
#dogs_filt = dogs_today[ (dogs_today.Track.isin(['Albion Park'])) & (dogs_today.DogName_bf.isin(['DULCERIA','FARMOR MILLES'])) ]
df.dogs_filt_ft = df.dogs_today[ (dogs_today.Track.isin(['Albion Park'])) & (dogs_today.RaceNum.isin(['2'])) ]

dogs_filt_bf = df.runners[ (df.runners.event_venue.isin(['Albion Park'])) & (df.runners.race_number.isin(['8'])) ]





