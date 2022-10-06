
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

 
#df.races_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\races_today_20220531_132pm.csv')
#df.races_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\races_today_live_2022_06_01_07_36.csv')
df.races_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\ft_races_today_live_2022_06_06_18_29.csv')
summ.races_live = hd.describe_df(df.races_live)

#df.dogs_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\dogs_today_20220531_132pm.csv')
#df.dogs_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\dogs_today_live_2022_06_01_07_36.csv')
df.dogs_live = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Live\\ft_dogs_today_live_2022_06_06_18_29.csv')
summ.dogs_live = hd.describe_df(df.dogs_live)

df.live_merge = pd.merge( df.dogs_live, df.races_live, left_on = 'RaceId', right_on = '@id', how = 'left' )
summ.live_merge = hd.describe_df(df.live_merge)


#----------------------------------------------------------------- IMPORT PAST LISTINGS -----------------------------------------------------------------


#df.races_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220531.csv')
#df.races_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220531.csv')
#df.races_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220601.csv')
df.races_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220606.csv')
summ.races_past = hd.describe_df(df.races_past)

#df.dogs_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220531.csv')
#df.dogs_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220531.csv')
#df.dogs_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220601.csv')
df.dogs_past = pd.read_csv(f'C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220606.csv')
summ.dogs_past = hd.describe_df(df.dogs_past)

df.past_merge = pd.merge( df.dogs_past, df.races_past, left_on = 'RaceId', right_on = '@id', how = 'left' )
summ.past_merge = hd.describe_df(df.past_merge)


#----------------------------------------------------------------- MERGE -----------------------------------------------------------------

df.live_merge_top = df.live_merge.head(100)
df.past_merge_top = df.past_merge.head(100)

print(df.live_merge.columns.values.tolist())
print(df.past_merge.columns.values.tolist())


df.main_merge_interim = pd.merge(
    df.live_merge[['RaceBox','DogName','Odds','Rating','Speed','RaceId','RaceNum','RaceName','RaceTime','Distance','RaceGrade','Track','Date']],
    df.past_merge[['Place','DogName','Box','RaceId','TrainerId','RaceNum','RaceName','RaceTime','Distance','RaceGrade','Track','date']],
    on = ['DogName','RaceId','RaceName'],
    how = 'left' ,
    suffixes = ['_LIVE','_PAST']
    )
summ.main_merge_interim = hd.describe_df(df.main_merge_interim)


#----------------------------------------------------------------- Fix Place Information -----------------------------------------------------------------

df.main_merge_interim.loc[:,"place_fix"] = df.main_merge_interim.apply( lambda x: str(x['Place']).replace('=',''), axis = 1 )
print(df.main_merge_interim.place_fix.value_counts())

df.races_dog_count = df.main_merge_interim[~df.main_merge_interim.Place.isin(['T','F','S'])].groupby(by = ['RaceId']).agg({'DogName':'count'}).reset_index().rename(columns = {'DogName':'NumDogs'})

df.main_merge = pd.merge(df.main_merge_interim, df.races_dog_count, on = 'RaceId', how = 'left')
summ.main_merge = hd.describe_df(df.main_merge)

#----------------------------------------------------------------- Find RaceIds w missing Place  -----------------------------------------------------------------

print(df.main_merge_interim.place_fix.value_counts(dropna = False))

raceids_w_missing_placeinfo = df.main_merge[ ( df.main_merge.place_fix.isin(['nan']) ) ]['RaceId'].unique()

#----------------------------------------------------------------- Find RaceIds with no Odds -----------------------------------------------------------------

# Find RaceIds with No Odds
raceids_w_missing_odds = df.main_merge[ ( df.main_merge.Odds.isna() ) ]['RaceId'].unique()
print(len(raceids_w_missing_odds))
# 88 races with missing odds

#----------------------------------------------------------------- Remove Missing data  -----------------------------------------------------------------



df.main_test_final = df.main_merge[ ~df.main_merge.RaceId.isin(list(raceids_w_missing_odds) + list(raceids_w_missing_placeinfo)) ]

print( len(df.main_merge.Track_LIVE.unique()) )
# 15 races
print( len(df.main_test_final.Track_LIVE.unique()) )
# 4 races


print( df.main_test_final.Track_LIVE.unique() )
''' ['Sandown Park' 'Warragul' 'Shepparton' 'Horsham'] '''
''' ['Shepparton' 'Traralgon' 'Horsham' 'Ballarat'] '''


print( len(df.main_merge.RaceId.unique()) )
# 160 races
print( len(df.main_test_final.RaceId.unique()) )
# 47 races





# UNDERSTAND MISSING DATA #
#df.main_merge.groupby()

print(df.main_merge.columns.values.tolist())

#grouping = ['RaceTime_LIVE']
grouping = ['Track_LIVE']

info_miss = df.main_merge.groupby( grouping )['Odds'].apply(lambda x: x.isnull().sum()).reset_index().rename( columns = {'Odds':'MissingOdds'} )
info_tota = df.main_merge.groupby( grouping ).agg( {'Odds':'count'} ).reset_index()
info = pd.merge(info_miss, info_tota, on = grouping , how = 'left')

print(df.main_merge.shape)

'''
01 June 07 37 Am

             Track_LIVE  MissingOdds  Odds
0           Albion Park          109     0
1              Ballarat            0    94
2               Bendigo            0   100
3            Cannington          104     0
4              Capalaba           81     0
5                Darwin           60     0
6                Gawler          101     0
7         Meadows (MEP)            0    84
8   Palmerston Nth (NZ)           70     0
9              Richmond          109     0
10          Rockhampton           78     0
11                Taree          105     0
12            Traralgon            0   105
13       Wentworth Park           68     0


02 June 07 07 Am

           Track_LIVE  MissingOdds  Odds
0         Albion Park           94     0
1          Angle Park           76     0
2              Casino          112     0
3   Christchurch (NZ)          120     0
4               Dapto           78     0
5              Gawler            2     0
6            Gunnedah          116     0
7              Hobart           97     0
8             Horsham            0    78
9            Mandurah          114     0
10      Mount Gambier          111     0
11       Sandown Park            0    81
12         Shepparton            0    98
13       Waikato (NZ)           91     0
14           Warragul            0    93

'''


#----------------------------------------------------------------- STRATEGY VARIABLES -----------------------------------------------------------------

print(df.main_test_final.columns.values.tolist())

#print(df.main_test_final.Place.value_counts())
print(df.main_test_final.place_fix.value_counts())


df.main_test_final.loc[:,"NumOdds"] = df.main_test_final.apply(lambda x : None if pd.isna(x.Odds) else x['Odds'].replace('$','') , axis = 1)
df.main_test_final["NumOdds"] = df.main_test_final["NumOdds"].astype(float)

df.main_test_final.sort_values(by = ['RaceId', 'NumOdds'], inplace = True)


df.main_test_final.loc[:,"ExpPos"] = df.main_test_final.groupby( ['RaceId'] )['NumOdds'].rank("dense", ascending=True)

#df.main_test_final.loc[:,"NumPlace"] = df.main_test_final["Place"].astype(int)
df.main_test_final.loc[:,"PlaceInterim"] = df.main_test_final.apply(lambda x : None if pd.isna(x.Place) else x['Place'].replace('=','') , axis = 1)

df.main_test_final.loc[:,"NumPlace"] = df.main_test_final.apply(lambda x : None if pd.isna(x.PlaceInterim) else 10 if x.PlaceInterim in ['S','T','F'] else int(x.PlaceInterim), axis = 1)

summ.main_test_final = hd.describe_df(df.main_test_final)



#----------------------------------------------------------------- PROFITABILITY VARIABLES -----------------------------------------------------------------

# Expected
df.main_test_final.loc[:,'flag_exptop3'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos <= 3 else False, axis = 1)
df.main_test_final["flag_exptop3"] = df.main_test_final["flag_exptop3"].astype(bool)



df.main_test_final.loc[:,'flag_expfav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos <= 1 else False, axis = 1)
df.main_test_final["flag_expfav"] = df.main_test_final["flag_expfav"].astype(bool)

df.main_test_final.loc[:,'flag_expsecfav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 2 else False, axis = 1)
df.main_test_final["flag_expsecfav"] = df.main_test_final["flag_expsecfav"].astype(bool)

df.main_test_final.loc[:,'flag_expthifav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 3 else False, axis = 1)
df.main_test_final["flag_expthifav"] = df.main_test_final["flag_expthifav"].astype(bool)

df.main_test_final.loc[:,'flag_expfoufav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 4 else False, axis = 1)
df.main_test_final["flag_expfoufav"] = df.main_test_final["flag_expfoufav"].astype(bool)

df.main_test_final.loc[:,'flag_expfoufav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 4 else False, axis = 1)
df.main_test_final["flag_expfoufav"] = df.main_test_final["flag_expfoufav"].astype(bool)

df.main_test_final.loc[:,'flag_expfiffav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 5 else False, axis = 1)
df.main_test_final["flag_expfiffav"] = df.main_test_final["flag_expfiffav"].astype(bool)

df.main_test_final.loc[:,'flag_expsixfav'] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.ExpPos) else True if x.ExpPos == 6 else False, axis = 1)
df.main_test_final["flag_expsixfav"] = df.main_test_final["flag_expsixfav"].astype(bool)


# Actuals
df.main_test_final.loc[:,"flag_win"] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.NumPlace) else True if x.NumPlace <= 1 else False, axis = 1)
df.main_test_final["flag_win"] = df.main_test_final["flag_win"].astype(bool)

df.main_test_final.loc[:,"flag_plc"] = df.main_test_final.apply(lambda x : np.nan if pd.isna(x.NumPlace) \
                                                                else True if (x.NumDogs >= 8) & (x.NumPlace <= 3) \
                                                                    else True if (x.NumDogs >= 5) & (x.NumPlace <= 2) \
                                                                        else False if (x.NumDogs < 5) \
                                                                            else False, axis = 1)    
df.main_test_final["flag_plc"] = df.main_test_final["flag_plc"].astype(bool)



# Add as strategy Numbers
#df.main_test_final.loc[:,"s2_1"] = ( df.main_test_final.flag_exptop3 ) # Don't Have Place Prices - Need to convert the Win Odds to Place Odds

df.main_test_final.loc[:,"s2_31"] = ( df.main_test_final.flag_expfav )
df.main_test_final.loc[:,"s2_32"] = ( df.main_test_final.flag_expsecfav )
df.main_test_final.loc[:,"s2_33"] = ( df.main_test_final.flag_expthifav )
df.main_test_final.loc[:,"s2_34"] = ( df.main_test_final.flag_expfoufav )
df.main_test_final.loc[:,"s2_35"] = ( df.main_test_final.flag_expfiffav )
df.main_test_final.loc[:,"s2_36"] = ( df.main_test_final.flag_expsixfav )


#----------------------------------------------------------------- PROFITABILITY -----------------------------------------------------------------

#strategies_2 = [ '2_1' , '2_3', '2_32', '2_33', '2_34']
strategies_2 = [ '2_31', '2_32', '2_33', '2_34', '2_35', '2_36']

finalres = pd.DataFrame( columns = ['strategy','races','bets','profit','profitability'] )

for strat in strategies_2:
    df.main_test_final.loc[:,'p'+ strat] = df.main_test_final.apply(lambda x : x.NumOdds - 1 if ( x['s'+strat] == x['flag_win'] ) & (x['s'+strat])\
                                        else -1 if ~( x['s'+strat] == x['flag_win'] ) & (x['s'+strat]) \
                                            else 0
                                    , axis=1)

    # Adding the Necessary cols
    bets = df.main_test_final['s'+strat].sum()
    races = len(df.main_test_final.RaceId.unique())
    profit = df.main_test_final['p'+strat].sum()
    profitability = round(float(profit/ bets)*100,1)
    
    row_input = [strat, races, bets, profit, str(profitability) + '%' ]
    
    finalres.loc[len(finalres)] = row_input




#----------------------------------------------------------------- SPLITS -----------------------------------------------------------------

sp1 = df.main_test_final.groupby( ['Track_LIVE'] ).agg({ 'RaceId':'nunique'\
                                                      ,'s2_31':'sum', 'p2_31':'sum','s2_32':'sum', 'p2_32':'sum','s2_33':'sum', 'p2_33':'sum'\
                                                          ,'s2_34':'sum', 'p2_34':'sum', 's2_35':'sum', 'p2_35':'sum' ,'s2_36':'sum', 'p2_36':'sum'})





