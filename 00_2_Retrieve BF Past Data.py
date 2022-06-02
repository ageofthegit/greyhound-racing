# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 13:21:44 2022

@author: karan
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


my_username = "kdsbhatti@gmail.com"
my_password = "B3tf@1rp@ss"
my_app_key = "U9o0IvlKooTsPHsv"


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


greyhounds_events_today.head()

greyhounds_events_today = greyhounds_events_today[greyhounds_events_today['Event Venue'].isin(tracks_today)]

greyhounds_events_today.head()

#----------------------------------------------------------------- Greyhound Market Catalogue -----------------------------------------------------------

market_catalogue_filter = filters.market_filter(
    event_ids = list(greyhounds_events_today['Event ID']),
    market_type_codes = ['WIN']
)


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
runners_df = pd.DataFrame(runners)


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
runners_df['runner_name'] = runners_df['runner_name'].apply(lambda x: x[(x.find(" ") + 1):].upper())

# Merge on the race number and event venue onto runners_df
runners_df = runners_df.merge(
     win_markets_df[['market_id', 'event_venue', 'race_number']],
     how = 'left',
     on = 'market_id')

print(runners_df.head())
















