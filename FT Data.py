# -*- coding: utf-8 -*-
"""
Created on Thu May 12 18:08:32 2022

@author: karan
"""

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
greys = ft.Fasttrack(fasttrack_key)

track_codes = greys.listTracks()
print(track_codes.head())

print(track_codes.state.value_counts())


#tracks_filter = list(track_codes[track_codes['state'] == 'QLD']['track_code'])
#print(len(tracks_filter)) 13
tracks_filter = list(track_codes['track_code'])
print(len(tracks_filter)) # 115


race_details, dog_results = greys.getRaceResults('2020-12-31', '2022-01-01', tracks_filter)
#race_details, dog_results = greys.getRaceResults('2018-01-01', '2021-06-15')


print(type(race_details))
print(type(dog_results))

print(race_details.columns.values.tolist())
print(dog_results.columns.values.tolist())

print(race_details.shape)
print(dog_results.shape)


race_details.to_csv("C:\\Users\\karan\\Documents\\Data\\racing\\race_details_20210101_20211231.csv", index = False)

dog_results.to_csv("C:\\Users\\karan\\Documents\\Data\\racing\\dog_results_20210101_20211231.csv", index = False)



