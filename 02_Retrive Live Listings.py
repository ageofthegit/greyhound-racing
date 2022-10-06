
# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

"""

OUTLINES
    a) Outline is to retrieve live listings

DETAILS
    a) The idea is to retrieve live listings from Ft
    b) from BF
    c) Find a way to calculate the SP or BSP and bet on it

NEXT STEPS    
    - Either get rid of races with missing values
    - Change the names of the Track to what they ought to be, and then do another merge

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

import betfairlightweight
from betfairlightweight import filters

import fasttrack as ft


#----------------------------------------------------------------- HELPFUL FUNCTIONS -----------------------------------------------------------------


#----------------------------------------------------------------- ENVIRONMENT VARIABLES FOR ACCESS -----------------------------------------------------------------

import os

#FUTURES_API_KEY = os.environ.get('FUTURES_API_KEY')
FASTTRACK_KEY = os.environ.get('FASTTRACK_KEY')


#----------------------------------------------------------------- RETRIEVE LIVE LISTINGS -----------------------------------------------------------------

greys = ft.Fasttrack(FASTTRACK_KEY)

track_codes = greys.listTracks()
track_codes.head()

print(track_codes.state.value_counts())

tracks_filter = list(track_codes['track_code'])
print(len(tracks_filter))

#races_today, dogs_today = greys.getBasicFormat('2022-06-01', tracks_filter)

filename_suffix = datetime.today().strftime('%Y_%m_%d_%H_%M')

df.ft_races_today, df.ft_dogs_today = greys.getFullFormat('2022-06-07', tracks = tracks_filter)


print(df.ft_races_today.columns.values.tolist())


df.ft_races_today.loc[:,'racetime_fix'] = pd.to_datetime(df.ft_races_today['RaceTime'], format='%I:%M%p').dt.strftime('%H:%M:%S')

print(filename_suffix)

df.ft_races_today.to_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\ft_races_today_live_{filename_suffix}.csv', index = False)
df.ft_dogs_today.to_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\ft_dogs_today_live_{filename_suffix}.csv', index = False)

#Test tomorrow if the price from fastrack was good enought for profits

#----------------------------------------------------------------- RETRIEVE LIVE LISTINGS -----------------------------------------------------------------
