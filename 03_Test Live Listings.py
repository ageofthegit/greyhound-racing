
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

"""
OUTLINES
    a) Import Live Listings 
    b) Import Result Data
    c) Merge and Test the hypothesis

DETAILS

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

import betfairlightweight
from betfairlightweight import filters

import fasttrack as ft


#----------------------------------------------------------------- IMPORT LIVE LISTINGS -----------------------------------------------------------------


df.races_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\races_today_20220531_132pm.csv')
summ.races_live = hd.describe_df(df.races_live)

df.dogs_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\dogs_today_20220531_132pm.csv')
summ.dogs_live = hd.describe_df(df.dogs_live)


df.live_merge = pd.merge( df.dogs_live, df.races_live, left_on = 'RaceId', right_on = '@id', how = 'left' )
summ.live_merge = hd.describe_df(df.live_merge)


#----------------------------------------------------------------- IMPORT PAST LISTINGS -----------------------------------------------------------------


df.races_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220531.csv')
summ.races_past = hd.describe_df(df.races_past)

df.dogs_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220531.csv')
summ.dogs_past = hd.describe_df(df.dogs_past)

df.past_merge = pd.merge( df.dogs_past, df.races_past, left_on = 'RaceId', right_on = '@id', how = 'left' )
summ.past_merge = hd.describe_df(df.past_merge)


#----------------------------------------------------------------- MERGE -----------------------------------------------------------------

df.live_merge_top = df.live_merge.head(100)
df.past_merge_top = df.past_merge.head(100)


print(df.live_merge.columns.values.tolist())

print(df.past_merge.columns.values.tolist())


df.main_merge = pd.merge(
    df.live_merge[['RaceBox','DogName','Odds','Rating','Speed','RaceId','RaceNum','RaceName','RaceTime','Distance','RaceGrade','Track','Date']],
    df.past_merge[['Place','DogName','Box','RaceId','TrainerId','RaceNum','RaceName','RaceTime','Distance','RaceGrade','Track','date']],
    on = ['DogName','RaceId','RaceName'],
    how = 'left' ,
    suffixes = ['LIVE_','PAST_']
    )

summ.main_merge = hd.describe_df(df.main_merge)


# Find RaceIds with No Odds
raceids_w_missingodds = df.main_merge[ ( df.main_merge.Odds.isna() ) ]['RaceId'].unique()
print(len(raceids_w_missingodds))

df.main_df = df.main_merge[ ~df.main_merge.RaceId.isin(raceids_w_missingodds) ]

print( len(df.main_merge.RaceId.unique()) )
print( len(df.main_df.RaceId.unique()) )


#----------------------------------------------------------------- STRATEGY VARIABLES -----------------------------------------------------------------

print(df.main_df.columns.values.tolist())

print(df.main_df.Place.value_counts())

df.main_df.sort_values(by = ['RaceId', 'NumOdds'], inplace = True)

df.main_df.loc[:,"NumOdds"] = df.main_df.apply(lambda x : None if pd.isna(x.Odds) else x['Odds'].replace('$','') , axis = 1)
df.main_df["NumOdds"] = df.main_df["NumOdds"].astype(float)

df.main_df.loc[:,"ExpPos"] = df.main_df.groupby( ['RaceId'] )['NumOdds'].rank("dense", ascending=True)

#df.main_df.loc[:,"NumPlace"] = df.main_df["Place"].astype(int)
df.main_df.loc[:,"PlaceInterim"] = df.main_df.apply(lambda x : None if pd.isna(x.Place) else x['Place'].replace('=','') , axis = 1)

df.main_df.loc[:,"NumPlace"] = df.main_df.apply(lambda x : None if pd.isna(x.PlaceInterim) else 10 if x.PlaceInterim in ['S','T','F'] else int(x.PlaceInterim), axis = 1)

summ.main_merge = hd.describe_df(df.main_df)

#----------------------------------------------------------------- PROFITABILITY VARIABLES -----------------------------------------------------------------

df.main_df.loc[:,'flag_exptop3'] = df.main_df.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos <= 3 else False, axis = 1)
df.main_df.loc[:,"flag_exptop3"] = df.main_df["flag_top3"].astype(bool)


df.main_df.loc[:,"flag_plc"] = df.main_df.apply(lambda x : np.nan if pd.isna(x.NumPlace) else True if x.NumPlace <= 3 else False, axis = 1)
df.main_df.loc[:,"flag_plc"] = df.main_df["flag_plc"].astype(bool)



df.main_df.loc[:,"s2_1"] = ( df.main_df.flag_exptop3 )


#----------------------------------------------------------------- PROFITABILITY -----------------------------------------------------------------

strategies_2 = ['2_1']

finalres = pd.DataFrame( columns = ['strategy','races','bets','profit','profitability'] )

for strat in strategies_2:
    df.main_df.loc[:,'p'+ strat] = df.main_df.apply(lambda x : x.NumOdds - 1 if ( x['s'+strat] == x['flag_plc'] ) & (x['s'+strat])\
                                        else -1 if ~( x['s'+strat] == x['flag_plc'] ) & (x['s'+strat]) \
                                            else 0
                                    , axis=1)

    # Adding the Necessary cols
    bets = df.main_df['s'+strat].sum()
    races = len(df.main_df.RaceId.unique())
    profit = df.main_df['p'+strat].sum()
    profitability = round(float(profit/ bets)*100,1)
    
    row_input = [strat, races, bets, profit, str(profitability) + '%' ]
    
    finalres.loc[len(finalres)] = row_input










