# -*- coding: utf-8 -*-
"""
Created on Thu May 12 18:08:32 2022

@author: karan
"""

# Adding the racing folder to the PATH variable 
import sys
#sys.path.append('C:\\Users\\karan\\Documents\\Code\\racing')
sys.path.append('C:\\Users\\karan\\Documents\\Racing\\greyhound-racing\\code-helpdesk')
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
FASTTRACK_KEY = os.environ.get('FASTTRACK_KEY')


#----------------------------------------------------------------- DOWNLOAD PAST LISTINGS -----------------------------------------------------------------

greys = ft.Fasttrack(FASTTRACK_KEY)

track_codes = greys.listTracks()
print(track_codes.head())

print(track_codes.state.value_counts())


#tracks_filter = list(track_codes[track_codes['state'] == 'QLD']['track_code'])
#print(len(tracks_filter)) 13
tracks_filter = list(track_codes['track_code'])
print(len(tracks_filter)) # 113


#race_details, dog_results = greys.getRaceResults('2022-05-31', '2022-05-31', tracks_filter)
#race_details, dog_results = greys.getRaceResults('2022-06-02', '2022-06-02', tracks_filter)

#race_details, dog_results = greys.getRaceResults('2022-01-01', '2022-09-30', tracks_filter)

#race_details, dog_results = greys.getRaceResults('2022-07-01', '2022-09-30', tracks_filter)

race_details, dog_results = greys.getRaceResults('2023-05-01', '2023-05-07', tracks_filter)

print(type(race_details))
print(type(dog_results))

print(race_details.columns.values.tolist())
print(dog_results.columns.values.tolist())

print(race_details.shape)
print(dog_results.shape)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220531.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220531.csv" , index = False)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220606.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220606.csv" , index = False)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_2022Q1_2022Q2.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220Q1_2022Q2.csv" , index = False)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_2021Q1_2021Q4.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_2021Q1_2021Q4.csv" , index = False)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\race_details_2023Q1.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\dog_results_2023Q1.csv" , index = False)

#race_details.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\race_details_2023M4.csv" , index = False)
#dog_results.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\dog_results_2023M4.csv" , index = False)

race_details.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\race_details_2023M5W1.csv" , index = False)
dog_results.to_csv( "C:\\Users\\karan\\Documents\\Racing\\greyhound-racing-data-fasttrack\\Past\\dog_results_2023M5W1.csv" , index = False)

#----------------------------------------------------------------- IMPORT PAST LISTINGS -----------------------------------------------------------------

