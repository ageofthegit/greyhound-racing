
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

"""
OUTLINES
    a) Import BF Data and Merge
    b) Import FT Data and Merge
    c) Combine BF & FT Data based on Key

DETAILS
    a) Import BF Data and Merge
        Import BF Win Data
        Import BF Place Data
        Add ['DogName', 'Track', 'EventDt'] columns for merge with FT data, capitalise DogName for merge and remove special characters
        Remove RACES where the Place data is missing
        Remove Non-Australian Data
        Remove corrupt Box data
        
        Mismatch Analysis - 
            Win has more data rows 322,471 vs Place data of 315,725 which is approximately a difference of 6746 rows \
            Can't do anymore mapping but remove missing races

        Fix Track names to merge on with FT Later

        
    b) Import FT Data and Merge
        Import Results Data
        Import Racing Data
        Replace special characters in DogName with nothing and capitalise them for merge
        Change Track name to match up with BF Data
        

    c) Find the merge key
        so far the ['MENU_HINT','Event_Dt','Track'] is giving the best merge.
            # Checking the Merge on 1 Months worth of data
                0.445% Mismatch on the 22696 rows

    

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

#df.win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = True, check_for_word = '2021.', DEBUG = False)
#del df.win_raw

#----------------------------------------------------------------- DATA IMPORT -----------------------------------------------------------------

#----------------------------------------------------------------- Betfair Data -----------------------------------------------------------------

#df.win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = False , check_for_word = '122021.', DEBUG = False)
#df.win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = True, check_for_word = '2021.', DEBUG = False)
df.win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = True, check_for_word = '2022.c', DEBUG = False)
if DEBUG : print(df.win_raw.shape)
# 55,537 for 2021 DEC
# 651,129 for 2021

summ.win_raw = hd.describe_df(df.win_raw) # 18 missing values in the whole year! Drop!!

df.win = df.win_raw[ df.win_raw.MENU_HINT.str.contains('AUS', na = False) ]
if DEBUG : print(df.win.shape) 
# 28,133 for 2021 DEC
# 322,471 for 2021

summ.win = hd.describe_df(df.win)

del df.win_raw

df.win.loc[ :, "EVENT_DT_INTERIM"] = df.win.EVENT_DT.str.replace('/','-')
#evntdt_qc = df.win[ df.win.EVENT_DT.str.contains('/') ][ ["EVENT_DT","EVENT_DT_FIX"] ]

df.win.loc[ :, "EVENT_DT_FIX"] = df.win.EVENT_DT_INTERIM.apply(lambda x : pd.to_datetime(x).date() )
# 02 53 PM

#print(df.win.dtypes)




#df.plc_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = False , check_for_word = '122021.', DEBUG = False)
#df.plc_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = True, check_for_word = '2021.', DEBUG = False)
df.plc_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = True, check_for_word = '2022.c', DEBUG = False)

if DEBUG : print(df.plc_raw.shape)
# 51,481 for 2021 DEC 
# 603,509 for 2021

summ.plc_raw = hd.describe_df(df.plc_raw)

df.plc = df.plc_raw[df.plc_raw.MENU_HINT.str.contains('AUS', na = False)]
if DEBUG : print(df.plc.shape)
# 27,565 for 2021 DEC
# 315,725 for 2021

summ.plc = hd.describe_df(df.plc)

df.plc.loc[ :, "EVENT_DT_INTERIM"] = df.plc.EVENT_DT.str.replace('/','-')
df.plc.loc[ :, "EVENT_DT_FIX"] = df.plc.EVENT_DT_INTERIM.apply(lambda x : pd.to_datetime(x).date() )

del df.plc_raw
#evntdt_qc = df.win[ df.win.EVENT_DT.str.contains('/') ][ ["EVENT_DT","EVENT_DT_FIX"] ]


#df.plc.columns
#qc = df.plc.groupby('EVENT_DT_FIX').agg({'EVENT_ID':'count'})
#df.plc_heads = df.plc.head(1000)

if DEBUG:
    print(df.win.shape)
    print(df.plc.shape)

    # Checking for overlap between the EVENT IDs 
    events_win = set(df.win.EVENT_ID.unique())
    selection_win = set(df.win.SELECTION_ID.unique())
    print(len(events_win ))
    
    events_plc = set(df.plc.EVENT_ID.unique())
    selection_plc = set(df.plc.SELECTION_ID.unique())
    print(len(events_plc ))
    
    interse_events = events_win.intersection(events_plc)
    print(len(interse_events))
    
    interse_selection = events_win.intersection(selection_plc)
    print(len(interse_selection))



    # Details for Merge
    print(df.win.columns.values.tolist())
    print(df.plc.columns.values.tolist())

    print(df.win.shape)
    print(df.plc.shape)


df.bf_raw = pd.merge(df.win, df.plc, on = ['MENU_HINT', 'EVENT_DT_FIX', 'SELECTION_NAME'] , how = 'left', suffixes=('_WIN', '_PLC'))\
                .sort_values(by = ['EVENT_DT_FIX', 'MENU_HINT', 'SELECTION_NAME'])\
                    .drop(columns = {'EVENT_DT_WIN', 'EVENT_DT_PLC'})
                    
summ.df_bf_raw = hd.describe_df(df.bf_raw)


'''

MISSING DATA ANALYSIS


df.bf_raw_left = pd.merge(df.win, df.plc, on = ['MENU_HINT', 'EVENT_DT_FIX', 'SELECTION_NAME'] , how = 'left', suffixes=('_WIN', '_PLC'))\
                .sort_values(by = ['EVENT_DT_FIX', 'MENU_HINT', 'SELECTION_NAME'])\
                    .drop(columns = {'EVENT_DT_WIN', 'EVENT_DT_PLC'})

df.bf_raw_outer = pd.merge(df.win, df.plc, on = ['MENU_HINT', 'EVENT_DT_FIX', 'SELECTION_NAME'] , how = 'outer', suffixes=('_WIN', '_PLC'))\
                .sort_values(by = ['EVENT_DT_FIX', 'MENU_HINT', 'SELECTION_NAME'])\
                    .drop(columns = {'EVENT_DT_WIN', 'EVENT_DT_INTERIM_WIN', 'EVENT_DT_PLC', 'EVENT_DT_INTERIM_PLC'})

df.bf_raw_right = pd.merge(df.win, df.plc, on = ['MENU_HINT', 'EVENT_DT_FIX', 'SELECTION_NAME'] , how = 'right', suffixes=('_WIN', '_PLC'))\
                .sort_values(by = ['EVENT_DT_FIX', 'MENU_HINT', 'SELECTION_NAME'])\
                    .drop(columns = {'EVENT_DT_WIN', 'EVENT_DT_PLC'})

if DEBUG: print(df.bf_raw.shape)
# 322,471 for 2021 from 323,473 - There is a nxn match


summ.br_raw_left = hd.describe_df(df.bf_raw_left)


missing_ids_win_all = df.bf_raw_outer[ df.bf_raw_outer.EVENT_ID_WIN.isna() ][ 'EVENT_ID_PLC' ].values.tolist()
print(len(missing_ids_win_all)) # 1,367, down to 22
missing_ids_win = df.bf_raw_outer[ df.bf_raw_outer.EVENT_ID_WIN.isna() ][ 'EVENT_ID_PLC' ].unique().tolist()
print(len(missing_ids_win)) # 195, down to 6


missing_ids_plc_all = df.bf_raw_outer[ df.bf_raw_outer.EVENT_ID_PLC.isna() ][ 'EVENT_ID_WIN' ].values.tolist()
print(len(missing_ids_plc_all)) # 8,111, down to 6766
missing_ids_plc = df.bf_raw_outer[ df.bf_raw_outer.EVENT_ID_PLC.isna() ][ 'EVENT_ID_WIN' ].unique().tolist()
print(len(missing_ids_plc)) # 1486, down to 1300


df.bf_raw_left_outer_miss = df.bf_raw_outer[ df.bf_raw_outer.EVENT_ID_WIN.isin(missing_ids_plc) | df.bf_raw_outer.EVENT_ID_PLC.isin(missing_ids_win) ]
print(df.bf_raw_left_outer_miss.shape) # 9994, down to 7321

summ.br_raw_left_miss = hd.describe_df(df.bf_raw_left_miss)


qc = df.plc[df.plc.MENU_HINT.isin(['AUS / Lism (AUS) 4th Jan'])]


rup_wins = df.win.groupby(['MENU_HINT','EVENT_DT_FIX']).agg({'EVENT_ID':'count'})
rup_plac = df.plc.groupby(['MENU_HINT','EVENT_DT_FIX']).agg({'EVENT_ID':'count'})


rup = rup_wins.merge(rup_plac, on = ['MENU_HINT','EVENT_DT_FIX'], how = 'outer')


print(missing_ids.shape)

summ.df_bf_raw = hd.describe_df(df.bf_raw)
print(df.bf_raw.shape)

summ.df_bf_raw_outer = hd.describe_df(df.bf_raw_outer)
print(df.bf_raw_outer.shape)

summ.df_bf_raw_right = hd.describe_df(df.bf_raw_right)
print(df.bf_raw_right.shape)


print(df.win.shape)
print(df.plc.shape)

FINAL - Win has more data rows 322471 vs Place data of 315725 which is approximately a difference of 6746 rows - Can't do anymore mapping but remove missing races

'''


#df.bf_raw.EVENT_NAME_PLC.value_counts(dropna = False)


# --------- Adding Columns of Interst to BF Data --------- 

# Example 30-11-2021 09:37
#df.bf_raw['Event_Dt'] = pd.to_datetime(df.bf_raw['EVENT_DT'], infer_datetime_format = True ).dt.date
#df.bf_raw['Event_Dt_a'] = pd.to_datetime(df.bf_raw['EVENT_DT_FIX'], format = '%d-%m-%Y %H:%M').dt.date
df.bf_raw['Event_Dt_fmt'] = pd.to_datetime(df.bf_raw['EVENT_DT_INTERIM_WIN'], format = '%d-%m-%Y %H:%M').dt.date


df.bf_raw.loc[:,"Box"] = df.bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[0].str.replace('.','')
df.bf_raw.loc[:,"Rug"] = df.bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[0].str.replace('.','')

df.bf_raw.loc[:,"DogName"] = df.bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[1].str.upper().replace(".","").replace("'","")

#qc_DogName_bf = df.bf.DogName.value_counts()

df.bf_raw[['country', 'race_track_details']] = df.bf_raw['MENU_HINT'].str.split('/', 1, expand = True )
df.bf_raw.loc[:,"country"] = df.bf_raw["country"].str.strip()

df.bf_raw[['Track', 'Event_Dt_MenuHint']] = df.bf_raw['race_track_details'].str.split('(', 1, expand = True )

df.bf_raw.loc[:,"Track"] = df.bf_raw["Track"].str.strip()

#df.bf_raw.loc[:,"Event_Dt_MenuHint"] = df.bf_raw["Event_Dt_MenuHint"].str.replace(r'\bAUS) \b','')
#df.bf_raw.loc[:,"Event_Dt_MenuHint_2"] = df.bf_raw["Event_Dt_MenuHint"].str.split(')', 1, expand = True)[1]


df.bf_raw.loc[:,"Day"]  = df.bf_raw.Event_Dt_MenuHint.str.extract(r'([0-9.]+)', expand = False).astype(int)
df.bf_raw.loc[:,"Year"]  = pd.to_datetime(df.bf_raw['Event_Dt_fmt']).dt.year
df.bf_raw.loc[:,"MonthName"]  = df.bf_raw.Event_Dt_MenuHint.str[-3:]
#df.bf_raw.loc[:,'Month'] = df.bf_raw['MonthName'].apply(lambda x: calendar.month_abbr[x])
df.bf_raw.loc[:,'Month'] = df.bf_raw['MonthName'].apply(lambda x: datetime.datetime.strptime(x, "%b").strftime("%m"))

df.bf_raw.loc[:,'Event_Dt'] = pd.to_datetime( df.bf_raw[['Year', 'Month', 'Day']]).dt.date




summ.df_bf_raw = hd.describe_df(df.bf_raw)
tracks_temp = df.bf_raw.Track.unique()

#Fix Track names to merge on with FT Later
df.bf_raw.loc[df.bf_raw.Track.isin(['The Meadows']), "Track"] = 'Meadows'

df.bf_raw.loc[df.bf_raw.Track.isin(['APrk']), "Track"] = 'Albion Park'
df.bf_raw.loc[df.bf_raw.Track.isin(['AnPk']), "Track"] = 'Angle Park'

df.bf_raw.loc[df.bf_raw.Track.isin(['Ball']), "Track"] = 'Ballarat'
df.bf_raw.loc[df.bf_raw.Track.isin(['Bath']), "Track"] = 'Bathurst'
df.bf_raw.loc[df.bf_raw.Track.isin(['Bend']), "Track"] = 'Bendigo'
df.bf_raw.loc[df.bf_raw.Track.isin(['Bull']), "Track"] = 'Bulli'
df.bf_raw.loc[df.bf_raw.Track.isin(['Bund']), "Track"] = 'Bundaberg'

df.bf_raw.loc[df.bf_raw.Track.isin(['Cann']), "Track"] = 'Cannington'
df.bf_raw.loc[df.bf_raw.Track.isin(['Capa']), "Track"] = 'Capalaba'
df.bf_raw.loc[df.bf_raw.Track.isin(['Casi']), "Track"] = 'Casino'
df.bf_raw.loc[df.bf_raw.Track.isin(['Cran']), "Track"] = 'Cranbourne'

df.bf_raw.loc[df.bf_raw.Track.isin(['Dapt']), "Track"] = 'Dapto'
df.bf_raw.loc[df.bf_raw.Track.isin(['Devn']), "Track"] = 'Devonport'
df.bf_raw.loc[df.bf_raw.Track.isin(['Dubb']), "Track"] = 'Dubbo'

df.bf_raw.loc[df.bf_raw.Track.isin(['Gawl']), "Track"] = 'Gawler'
df.bf_raw.loc[df.bf_raw.Track.isin(['Geel']), "Track"] = 'Geelong'
df.bf_raw.loc[df.bf_raw.Track.isin(['Gosf']), "Track"] = 'Gosford'
df.bf_raw.loc[df.bf_raw.Track.isin(['Goul']), "Track"] = 'Goulburn'
df.bf_raw.loc[df.bf_raw.Track.isin(['Graf']), "Track"] = 'Grafton'
df.bf_raw.loc[df.bf_raw.Track.isin(['Gunn']), "Track"] = 'Gunnedah'

df.bf_raw.loc[df.bf_raw.Track.isin(['Heal']), "Track"] = 'Healesville'
df.bf_raw.loc[df.bf_raw.Track.isin(['Hoba']), "Track"] = 'Hobart'
df.bf_raw.loc[df.bf_raw.Track.isin(['Hshm']), "Track"] = 'Horsham'

df.bf_raw.loc[df.bf_raw.Track.isin(['Ipsw']), "Track"] = 'Ipswich'

df.bf_raw.loc[df.bf_raw.Track.isin(['Laun']), "Track"] = 'Launceston'
df.bf_raw.loc[df.bf_raw.Track.isin(['Lism']), "Track"] = 'Lismore'

df.bf_raw.loc[df.bf_raw.Track.isin(['MBdg']), "Track"] = 'Murray Bridge'
df.bf_raw.loc[df.bf_raw.Track.isin(['Mbdg']), "Track"] = 'Murray Bridge'
df.bf_raw.loc[df.bf_raw.Track.isin(['MGam']), "Track"] = 'Mount Gambier'
df.bf_raw.loc[df.bf_raw.Track.isin(['Mait']), "Track"] = 'Maitland'
df.bf_raw.loc[df.bf_raw.Track.isin(['Mand']), "Track"] = 'Mandurah'
df.bf_raw.loc[df.bf_raw.Track.isin(['Mead']), "Track"] = 'Meadows'

df.bf_raw.loc[df.bf_raw.Track.isin(['Nowr']), "Track"] = 'Nowra'

df.bf_raw.loc[df.bf_raw.Track.isin(['Rich']), "Track"] = 'Richmond'
df.bf_raw.loc[df.bf_raw.Track.isin(['Rock']), "Track"] = 'Rockhampton'

df.bf_raw.loc[df.bf_raw.Track.isin(['SPrk']), "Track"] = 'Sandown Park'
df.bf_raw.loc[df.bf_raw.Track.isin(['Shep']), "Track"] = 'Shepparton'

df.bf_raw.loc[df.bf_raw.Track.isin(['Tare']), "Track"] = 'Taree'
df.bf_raw.loc[df.bf_raw.Track.isin(['Temo']), "Track"] = 'Temora'
df.bf_raw.loc[df.bf_raw.Track.isin(['Town']), "Track"] = 'Townsville'

df.bf_raw.loc[df.bf_raw.Track.isin(['WPrk']), "Track"] = 'Wentworth Park'
df.bf_raw.loc[df.bf_raw.Track.isin(['Wagg']), "Track"] = 'Wagga'
df.bf_raw.loc[df.bf_raw.Track.isin(['Warr']), "Track"] = 'Warrnambool'
df.bf_raw.loc[df.bf_raw.Track.isin(['Wchp']), "Track"] = 'Wauchope'
df.bf_raw.loc[df.bf_raw.Track.isin(['Wgul']), "Track"] = 'Warragul'


df.bf_raw.loc[df.bf_raw.Track.isin(['Gard']), "Track"] = 'The Gardens'


tracks_temp_after = df.bf_raw.Track.unique().tolist()
tracks_temp_after.sort()

#APrk, Dapt
'''
lista = ['APrk', 'Albion Park', 'AnPk', 'Angle Park', 'Ball', 'Ballarat', 'Bath', 'Bathurst', 'Bend', 'Bendigo', 'Bull', 'Bulli', 'Bund', 'Bundaberg'\
         , 'Cann', 'Cannington', 'Capa', 'Capalaba', 'Casi', 'Casino', 'Cran', 'Cranbourne'\
             , 'Dapt', 'Dapto', 'Devn', 'Devonport', 'Dubb', 'Dubbo'\
                 , 'Gard', 'Gawl', 'Gawler', 'Geel', 'Geelong', 'Gosf', 'Gosford', 'Goul', 'Goulburn', 'Graf', 'Grafton', 'Gunn', 'Gunnedah'\
                     , 'Heal', 'Healesville', 'Hoba', 'Hobart', 'Horsham', 'Hshm'\
                         , 'Ipsw', 'Ipswich'\
                             , 'Laun', 'Launceston', 'Lism', 'Lismore'\
                                 , 'MBdg', 'MGam', 'Mait', 'Maitland', 'Mand', 'Mandurah', 'Mbdg', 'Mead', 'Meadows', 'Mount Gambier', 'Murray Bridge'\
                                     , 'Nowr', 'Nowra'\
                                         , 'Rich', 'Richmond', 'Rock', 'Rockhampton'\
                                             , 'SPrk', 'Sale', 'Sandown Park', 'Shep', 'Shepparton'\
                                                 , 'Tare', 'Taree', 'Temo', 'Temora', 'The Gardens', 'Town', 'Townsville'\
                                                     , 'WPrk', 'Wagg', 'Wagga', 'Warr', 'Warragul', 'Warrnambool', 'Wauchope', 'Wchp', 'Wentworth Park', 'Wgul']
print(lista)

'''


'''
Check if any other kind of Boxes Available in the BF Data

    a) Just Crap Data
        df.bf_raw.Box.value_counts()
        temp = df.bf_raw[ ~df.bf_raw.Box.isin(['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])]
        
    b) Clear out races that have missing data for 'Place'
        
'''


missing_menus_df = df.bf_raw.groupby('MENU_HINT').agg({'EVENT_NAME_PLC': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'EVENT_NAME_PLC':'miss'})
missing_menus = missing_menus_df[missing_menus_df.miss > 0].MENU_HINT.values.tolist()

# Filtering for a) Australian b) Only GH in the races
df.bf = df.bf_raw[ df.bf_raw.Box.isin(['1','2','3','4','5','6','7','8']) \
                  & df.bf_raw.country.isin(['AUS']) \
                      & ~(df.bf_raw.MENU_HINT.isin(missing_menus))]

if DEBUG : print(df.bf.shape) 
# 24220 for 2021 DEC
# 270500 for 2021
# 271885 for 2021

# 107042 in 2022 uptill May
    
df.bf.loc[:,"Box"] = df.bf["Box"].astype(float)

#df.bf_mg = df.bf[ df.bf.Rug.isin(['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']) & df.bf.country.isin(['AUS'])]
df.bf.loc[:,"Rug"] = df.bf["Rug"].astype(float)

summ.df_bf = hd.describe_df(df.bf)

print(len(df.bf_raw.MENU_HINT.unique().tolist()))
print(len(df.bf.MENU_HINT.unique().tolist()))

# 2021
# Lost about 3,437 / 4,053 races in the process of cleaning it up approx 15% of the races with missing Place Information

# 2022 Jan to 2022 May
# Lost about 1,348 / 1,902 races in the process of cleaning it up approx 30% of the races with missing Place Information




#----------------------------------------------------------------- Fast Track Data -----------------------------------------------------------------


'''

Place 
    1 to 8 
    In case the GH did not finish the race, but was in the box
        T - Tailed Off
        B - Stayed Back
        F - Fell
        P - Pulled Up        
        
        R ?
        S ?



'''


# Importing Dog Race Results

#res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20211201_20211231.csv')
df.res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\dog_results_20220101_20220531.csv')

df.res_raw.loc[:,"DogName"] = df.res_raw["DogName"].str.replace("'","").str.replace(".","")
if DEBUG: print(df.res_raw.shape) 
# 79,464


#if DEBUG: res_raw[ ~(res_raw.Place.isin( ['D','F','N','R','S','T',''])) ].shape # 66608
if DEBUG: print(df.res_raw[ ~(df.res_raw.Place.isin( ['R','S'])) ].shape) # 32,180

df.res_raw2 = df.res_raw[ ~(df.res_raw.Place.isin( ['R','S']))  ]
df.res_ = df.res_raw2[~df.res_raw2.Place.isna()]
if DEBUG: print(df.res_.shape) 
# 372,988

del df.res_raw, df.res_raw2

#res_ = res_raw


# Importing Race Details 
#race_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20211201_20211231.csv', parse_dates = True)
df.race_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\FastTrack\\Past\\race_details_20220101_20220531.csv', parse_dates = True)

df.race_raw['Event_Dt'] = pd.to_datetime(df.race_raw['date']).dt.date

#dtvalct = race_raw.Event_Dt.value_counts()


df.race_raw.loc[df.race_raw.Track.isin(['Murray Bridge (MBR)','Murray Bridge (MBS)']), "Track"] = 'Murray Bridge'
df.race_raw.loc[df.race_raw.Track.isin(['Richmond (RIS)']), "Track"] = 'Richmond'

df.race_raw.loc[df.race_raw.Track.isin(['Sandown (SAP)']), "Track"] = 'Sandown Park'

df.race_raw.loc[df.race_raw.Track.isin(['Meadows (MEP)']), "Track"] = 'Meadows'
df.race_raw.loc[df.race_raw.Track.isin(['The Meadows']), "Track"] = 'Meadows'


if DEBUG : print(df.race_raw.shape)

# 2021
# 52,103 Races

# 2022 upto May
# 21,002 Races


df.race_ = df.race_raw[ ~df.race_raw.Track.str.contains('NZ')]


if DEBUG : print(df.race_.shape)

del df.race_raw

if DEBUG: print(df.race_.dtypes)

if DEBUG:
    print(df.res_.columns.values.tolist())
    print(df.race_.columns.values.tolist())
    
    print(df.res_.shape)
    print(df.race_.shape)

df.ft = pd.merge(df.res_, df.race_, left_on = 'RaceId', right_on = '@id', how = 'inner', suffixes=('_DOG', '_RACE'))
if DEBUG: print(df.ft.shape)

# 2021
# 333,285

# 2022 upto May
# 132,558

#qc_DogName = df.ft_merg.DogName.value_counts()

summ.ft = hd.describe_df(df.ft)

#----------------------------------------------------------------- Sets Track a) BF b) FT Data -----------------------------------------------------------------

ft_trk = df.ft.Track.unique()

ft_track = set(df.ft.Track.unique())
print(len(ft_track))

bf_trk = df.bf[ df.bf.country.isin(['AUS'])].Track.unique()

bf_track = set(df.bf[ df.bf.country.isin(['AUS'])].Track.unique())
print(len(bf_track))

inters = ft_track.intersection(bf_track)
print(len(inters))

differs_ft = ft_track - bf_track
print(len(differs_ft))

differs_bf = bf_track - ft_track
print(len(differs_bf))


#----------------------------------------------------------------- Merge a) BF b) FT Data -----------------------------------------------------------------

'Try on Race Date + GH Name (which includes the gate number & Uppercase all)'

# Looking at FastTrack Dataset
pd.crosstab(df.ft.Rug, df.ft.Box, dropna= False)

# Merging the Datasets

#df.ft.shape
#df.ft[ df.ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape



'''
FAILED : Merge Key ['Event_Dt','DogName', 'Rug']

print(df.bf[ df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape)

df.final_rug = pd.merge( df.bf[ df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ]\
                    , df.ft[ df.ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ]\
                        , on = ['Event_Dt','DogName', 'Rug'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT_WIN','EVENT_NAME_WIN','SELECTION_NAME'])
summ.df.final_rug = hd.describe_df(df.final_rug)
print(df.final_rug.shape)
'''


'''
MERGE KEY : ['Event_Dt','DogName', 'Box']

print(df.bf.shape)
print(df.bf.Event_Dt.value_counts())

print(df.bf[ df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape) # 27,144

df.final_box = pd.merge( df.bf[ df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() & df.bf[ df.bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ]\
                    , df.ft[ df.ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() & df.ft['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ]\
                        , on = ['Event_Dt','DogName', 'Box'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])
summ.df.final_box = hd.describe_df(df.final_box)
# 6.12% Missing of 1,661 / 27,114 records

print(df.final_box.shape)
# 2560

'''


'''
TRY : Merge Key -> ['Event_Dt','DogName', 'Track']
'''

print(df.bf.shape)

# 2021
# 271,885

# 2022 upto May
# 107,042

# Checking the Merge on 1 Months worth of data

print(df.bf[ ( df.bf['Event_Dt'] >= datetime.datetime.strptime('2022-01-01' , "%Y-%m-%d").date() )\
            & ( df.bf['Event_Dt'] <= datetime.datetime.strptime('2022-05-31' , "%Y-%m-%d").date() ) \
                ].shape)

# 22,696 - December 2021
# 271,065 - 2021

# 2022 Upto May
# 106,307

df.final_v3 = pd.merge( df.bf[ (df.bf['Event_Dt'] >= datetime.datetime.strptime('2022-01-01' , "%Y-%m-%d").date() ) & (df.bf['Event_Dt'] <= datetime.datetime.strptime('2022-05-31' , "%Y-%m-%d").date() ) ]\
                    , df.ft[ (df.ft['Event_Dt'] >= datetime.datetime.strptime('2022-01-01' , "%Y-%m-%d").date() ) & ( df.ft['Event_Dt'] <= datetime.datetime.strptime('2022-05-31' , "%Y-%m-%d").date() )]\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(df.final_v3.shape)

# 2021
# 22,696 - NO nxn Match

# 2022 Upto May
# 106,037 

summ.df_final_v3 = hd.describe_df(df.final_v3)

#0.07% MISMATCH, 18 / 22,613 records 
#0.445% MISMATCH, 101 / 22,696 records 
#0.445% MISMATCH, 101 / 22,696 records 

#0.065% MISMATCH, 183 / 271,065 records 

# 2022 upto May
# 0.5% MISMATCH, 618 / 106,037 records 

print(df.final_v3.Place.value_counts())

df.algodata = df.final_v3[ (~df.final_v3.Place.isin(['F','T','nan','P','B','N','D']) ) & (~df.final_v3.Place.isna()) ] 

print(df.algodata.shape)
print(df.algodata.Place.value_counts())

# 2021
# 265805

# 2022 Upto May
# 104808

summ.df_algodata = hd.describe_df(df.algodata)


'''

df.final_v3.groupby( [ 'Box_x' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})
df.final_v3.groupby( [ 'Event_Dt' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})
df.final_v3.groupby( [ 'Track' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

mh = df.final_v3.groupby( [ 'MENU_HINT' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

print(mh[mh.miss > 0].MENU_HINT.values.tolist())



df.final_v3_outer = pd.merge( df.bf[ (df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & (df.bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ) ]\
                    , df.ft[ (df.ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & ( df.ft['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() )]\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'outer')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])


qc = df.final_v3_outer[df.final_v3_outer.Track.isin(['Richmond'])]

qc = df.final_v3_outer[df.final_v3_outer.MENU_HINT.isin( mh[mh.miss > 0].MENU_HINT.values.tolist() )]


print(df.final_v3.Track.unique().tolist())

df.final_v3.Place.value_counts()

'''


'''
find out duplicates and a logic to delete the redundant ones
    which is the correct box - the ones assigned with a number or a letter

'''


'''
#
qc = df.final[df.final.isna()]

df.final.Event_Dt.value_counts(dropna = False)



od_bf = df.bf[ df.bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-15' , "%Y-%m-%d").date() ]

od_ft = df.ft[ df.ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-15' , "%Y-%m-%d").date() ]


x1 = od_bf.Track.value_counts()
x2 = od_ft.Track.value_counts()

od_qc_left = pd.merge( od_bf \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_left.shape) # 388 FT Nans from 12456 rows, a missmath % of 3.115
summ.df.od_qc_left = hd.describe_df(od_qc_left)


od_qc_left.groupby( [ 'Box_x' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

pd.crosstab(od_qc_left.Box_x, od_qc_left.Box_y, dropna = False)

print(od_qc_left.Box_x.value_counts())
'''


'''
1.0     1606
2.0     1606
4.0     1597
8.0     1588
7.0     1580
3.0     1394
6.0     1388
5.0     1342
9.0      256
10.0      99
Name: Box_x, dtype: int64

'''

'''
od_qc_righ = pd.merge( od_bf_mg \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Box'] , how = 'right')\
                            .sort_values(by = ['MENU_HINT_WIN','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_righ.shape) # 958 rows , 217 Na
summ.df.od_qc_righ = hd.describe_df(od_qc_righ)

del od_qc_outer
del summ.df.od_qc_oute 

print(od_bf.Track.unique().tolist())
print(od_ft.Track.unique().tolist())


print(od_bf.columns.values.tolist())
print(od_ft.columns.values.tolist())

od_qc_outer = pd.merge( od_bf \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'outer')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_outer.shape) # 1264,
summ.df.od_qc_oute = hd.describe_df(od_qc_outer)

print(od_main_mg.Event_Dt.value_counts())

print(df.ft_merg.Event_Dt.value_counts())
print(df.ft_merg.EVENT_DT.value_counts())
'''


# 4 55 PM


#----------------------------------------------------------------- STRATEGY ANALYSIS -----------------------------------------------------------------

#----------------------------------------------------------------- Adding Columns -----------------------------------------------------------------

if DEBUG: print(df.algodata.shape)

# 2021 Data
# 271,065
# 268,505

# 2022 Upto May
# 104,808



# Expected

df.algodata.loc[:,"flag_fav"] = df.algodata["StartPrice"].apply(lambda x : np.nan if pd.isna(x) else True if 'F' in x else False )
df.algodata.loc[:,"flag_fav"] = df.algodata["flag_fav"].astype(bool)

df.algodata.loc[:,"StartPrice"] = df.algodata["StartPrice"].astype(str)
df.algodata.loc[:,"sp"] = df.algodata.apply( lambda x: np.nan if pd.isna(x.flag_fav) else x["StartPrice"].replace('F','').replace('$','') if x.flag_fav  else x["StartPrice"].replace('$','') , axis = 1 )
df.algodata.loc[:,"sp"] = df.algodata['sp'].astype(float)



df.algodata.loc[:,"RANK_"] = df.algodata.groupby( ['RaceId'] )['BSP_WIN'].rank("dense", ascending=True)


df.algodata.loc[:,"flag_top1"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ <= 1 else False, axis = 1)
df.algodata.loc[:,"flag_top1"] = df.algodata["flag_top1"].astype(bool)

df.algodata.loc[:,'flag_top2'] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ <= 2 else False, axis = 1)
df.algodata.loc[:,"flag_top2"] = df.algodata["flag_top2"].astype(bool)

df.algodata.loc[:,'flag_top3'] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ <= 3 else False, axis = 1)
df.algodata.loc[:,"flag_top3"] = df.algodata["flag_top3"].astype(bool)


df.algodata.loc[:,"flag_expfav"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ <= 1 else False, axis = 1)
df.algodata.loc[:,"flag_expfav"] = df.algodata["flag_expfav"].astype(bool)

df.algodata.loc[:,"flag_expsec"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 2 else False, axis = 1)
df.algodata.loc[:,"flag_expsec"] = df.algodata["flag_expsec"].astype(bool)

df.algodata.loc[:,"flag_expthi"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 3 else False, axis = 1)
df.algodata.loc[:,"flag_expthi"] = df.algodata["flag_expthi"].astype(bool)

df.algodata.loc[:,"flag_expfou"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 4 else False, axis = 1)
df.algodata.loc[:,"flag_expfou"] = df.algodata["flag_expfou"].astype(bool)

df.algodata.loc[:,"flag_expfif"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 5 else False, axis = 1)
df.algodata.loc[:,"flag_expfif"] = df.algodata["flag_expfif"].astype(bool)

df.algodata.loc[:,"flag_expsix"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 6 else False, axis = 1)
df.algodata.loc[:,"flag_expsix"] = df.algodata["flag_expsix"].astype(bool)

df.algodata.loc[:,"flag_expsev"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 7 else False, axis = 1)
df.algodata.loc[:,"flag_expsev"] = df.algodata["flag_expsev"].astype(bool)

df.algodata.loc[:,"flag_expeig"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.RANK_) else True if x.RANK_ == 8 else False, axis = 1)
df.algodata.loc[:,"flag_expeig"] = df.algodata["flag_expeig"].astype(bool)


# Actuals

if DEBUG: print(df.algodata.Place.value_counts())

df.algodata['Place'] = df.algodata['Place'].astype(str)
df.algodata.loc[:,"pos"] = df.algodata.apply( lambda x: x['Place'].replace('=',''), axis = 1 )

if DEBUG: print(df.algodata.pos.value_counts(dropna = False))


df.algodata.loc[:,"pos"] = df.algodata["pos"].astype(int)

df.algodata.loc[:,'flag_win'] = df.algodata.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 1 else False, axis = 1)
df.algodata.loc[:,'flag_win'] = df.algodata['flag_win'].astype(bool)

df.algodata.loc[:,'flag_top2'] = df.algodata.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 2 else False, axis = 1)
df.algodata.loc[:,'flag_top2'] = df.algodata['flag_top2'].astype(bool)

df.algodata.loc[:,"flag_plc"] = df.algodata.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 3 else False, axis = 1)
df.algodata.loc[:,"flag_plc"] = df.algodata["flag_plc"].astype(bool)


#----------------------------------------------------------------- Strategy Flags -----------------------------------------------------------------


'''

s1 - Strategy 1 (Favourite based strategies)
    1 Fav to win aka bet a $1 o the favourite    
        1 fav to win under/over 1.5
        2 fav to win under/over 2.0
        3 fav to win under/over 2.5
        4 fav to win under/over 3.0

    21 Fav to Win
    22 Sec Fav to Win
    23 Thi Fav to Win
    24 Fou Fav to Win
    25 Fif Fav to Win
    26 Six Fav to Win
    27 Sev Fav to Win
    28 Eig Fav to Win
    

s2 - Strategy 2 ( Top 3 Based Strategies )
    1 All top 3 to place 
    2 Any of the top 3 to win 
        bet on top 2 to win
        bet on top 3 to win, is that 
    31 Favourite to Place
    32 Sec Fav to Place
    33 Thi Fav to Place
    34 Fourth Fav to Place
    35 Fif Fav to Place
    36 Six Fav to Place 
    37 Sev Fav to Place
    38 Eigh Fav to Place
    

'''

#res_.loc[:,"s1_1"] = res_.apply(lambda x : (x.flag_fav) & (x.flag_win), axis = 1 )
df.algodata.loc[:,"s1_1"] = ( df.algodata.flag_top1 )

df.algodata.loc[:,"s1_11"] = ( df.algodata.flag_top1 ) & ( df.algodata.sp <= 1.5)
df.algodata.loc[:,"s1_12"] = ( df.algodata.flag_top1 ) & ( df.algodata.sp <= 2.0)
df.algodata.loc[:,"s1_13"] = ( df.algodata.flag_top1 ) & ( df.algodata.sp <= 2.5)
df.algodata.loc[:,"s1_14"] = ( df.algodata.flag_top1 ) & ( df.algodata.sp <= 3.0)

df.algodata.loc[:,"s1_21"] = ( df.algodata.flag_expfav )
df.algodata.loc[:,"s1_22"] = ( df.algodata.flag_expsec )
df.algodata.loc[:,"s1_23"] = ( df.algodata.flag_expthi )
df.algodata.loc[:,"s1_24"] = ( df.algodata.flag_expfou )
df.algodata.loc[:,"s1_25"] = ( df.algodata.flag_expfif )
df.algodata.loc[:,"s1_26"] = ( df.algodata.flag_expsix )
df.algodata.loc[:,"s1_27"] = ( df.algodata.flag_expsev )
df.algodata.loc[:,"s1_28"] = ( df.algodata.flag_expeig )


df.algodata.loc[:,"s2_1"] = ( df.algodata.flag_top3 )
#df.algodata.loc[:,"s2_2"] = ( df.algodata.flag_fav )

df.algodata.loc[:,"s2_31"] = ( df.algodata.flag_expfav )
df.algodata.loc[:,"s2_32"] = ( df.algodata.flag_expsec )
df.algodata.loc[:,"s2_33"] = ( df.algodata.flag_expthi )
df.algodata.loc[:,"s2_34"] = ( df.algodata.flag_expfou )
df.algodata.loc[:,"s2_35"] = ( df.algodata.flag_expfif )
df.algodata.loc[:,"s2_36"] = ( df.algodata.flag_expsix )
df.algodata.loc[:,"s2_37"] = ( df.algodata.flag_expsev )
df.algodata.loc[:,"s2_38"] = ( df.algodata.flag_expeig )

dty = df.algodata.dtypes


#----------------------------------------------------------------- Eval Metrics -----------------------------------------------------------------

'''

Evaluation Metrics 
    Hit Rate 
        # of times this flag has been hit / Total # of races 
        
    Profitability 
        If we spend $1 on the bet, how much are we expecting to win back
            Wins / Spend

'''

#strat = '1_1'


print(df.algodata.columns.values.tolist())

print(len(df.algodata.EVENT_ID_WIN.unique()))
print(len(df.algodata.MENU_HINT.unique()))

print(len(df.algodata.EVENT_ID_PLC.unique()))

print(df.algodata.shape)


algo_head = df.algodata.head()


strategies_1 = ['1_1', '1_11', '1_12', '1_13', '1_21', '1_22', '1_23', '1_24', '1_25', '1_26', '1_27', '1_28']
strategies_2 = ['2_1', '2_31', '2_32', '2_33', '2_34', '2_35', '2_36', '2_37', '2_38' ]


finalres = pd.DataFrame( columns = ['strategy','races','bets','profit','profitability'] )


for strat in strategies_1:
    df.algodata.loc[:,'p'+ strat] = df.algodata.apply(lambda x : x.BSP_WIN - 1 if ( x['s'+strat] == x['flag_win'] ) & (x['s'+strat])\
                                        else -1 if ~( x['s'+strat] == x['flag_win'] ) & (x['s'+strat]) \
                                            else 0
                                    , axis=1)

    # Adding the Necessary cols
    races = len(df.algodata.EVENT_ID_WIN.unique())
    bets = df.algodata['s'+strat].sum()
    profit = df.algodata['p'+strat].sum()
    profitability = round(float(profit/ bets)*100,1)
    
    row_input = [strat, races, bets, profit, str(profitability) + '%' ]
    
    finalres.loc[len(finalres)] = row_input
    

for strat in strategies_2:
    df.algodata.loc[:,'p'+ strat] = df.algodata.apply(lambda x : x.BSP_PLC - 1 if ( x['s'+strat] == x['flag_plc'] ) & (x['s'+strat])\
                                        else -1 if ~( x['s'+strat] == x['flag_plc'] ) & (x['s'+strat]) \
                                            else 0
                                    , axis=1)

    # Adding the Necessary cols
    races = len(df.algodata.EVENT_ID_WIN.unique())
    bets = df.algodata['s'+strat].sum()
    profit = df.algodata['p'+strat].sum()
    profitability = round(float(profit/ bets)*100,1)
    
    row_input = [strat, races, bets, profit, str(profitability) + '%' ]
    
    finalres.loc[len(finalres)] = row_input
    


#----------------------------------------------------------------- Quality Checking Strategies  -----------------------------------------------------------------


print(df.algodata.columns.values)

print(df.algodata.Month.value_counts())

algo_sample = df.algodata[ df.algodata.Month.isin(['02']) ]


#----------------------------------------------------------------- Stability  -----------------------------------------------------------------


print(df.algodata.columns.values.tolist())

algo_sample.groupby('EVENT_DT_FIX').agg({'p2_3':'sum'}).plot()

algo_sample.groupby(['Month','Day']).agg({'p2_3':'sum', 's2_1':'sum'}).plot(kind = 'bar')

algo_sample.groupby(['Month','Day']).agg({'p2_3':'sum', 's2_1':'sum'}).plot(kind = 'bar')


df.algodata.groupby(['Track']).agg({'p2_31':'sum', 's1_1':'sum'}).plot(kind = 'bar')

df.algodata.groupby(['Track']).agg({'p2_32':'sum', 's1_1':'sum'}).plot(kind = 'bar')
df.algodata.groupby(['Track']).agg({'p2_33':'sum', 's1_1':'sum'}).plot(kind = 'bar')

df.algodata.groupby(['Track']).agg({'p1_11':'sum', 's1_1':'sum'}).plot(kind = 'bar')

#----------------------------------------------------------------- Stability  -----------------------------------------------------------------

print(df.algodata.Place.value_counts(dropna=False))

temp = df.algodata[df.algodata.Place.isna()]
 
print(df.algodata.shape)

eda1 = df.algodata.groupby(['Place','flag_fav'], dropna= False).agg({'@id':'count'}, dropna = False).unstack(level=1)

df.algodata.sp.plot(kind = 'hist', bins = 50)

df.algodata['Place'].value_counts()

df.algodata['flag_top3'] = res_.apply( lambda x: True if x.Place <=3 else False , axis = 1 )





#----------------------------------------------------------------- EXPLORATORY DATA ANALYSIS -----------------------------------------------------------------

summ.res = hd.describe_df(res_)


