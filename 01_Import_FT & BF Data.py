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
        
    b) Import FT Data and Merge
        Import Results Data
        Import Racing Data
        Replace special characters in DogName with nothing and capitalise them for merge
        Change Track name to match up with BF Data
        

    c) Find the merge key
        so far the ['MENU_HINT','Event_Dt','Track'] is giving the best merge.
    

NEXT STEPS


    
    - Either get rid of races with missing values


"""



import pandas as pd, numpy as np, calendar

import helpdesk as hd

import datetime

DEBUG = True

#----------------------------------------------------------------- DATA IMPORT -----------------------------------------------------------------

#----------------------------------------------------------------- Betfair Data -----------------------------------------------------------------

#df_win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = False , check_for_word = '122021.', DEBUG = False)
df_win_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = True, check_for_word = '2021.', DEBUG = False)
if DEBUG : print(df_win_raw.shape) 
# 55,537 for 2021 DEC
# 651,129 for 2021

summ_win_raw = hd.describe_df(df_win_raw) # 18 missing values in the whole year! Drop!!

df_win = df_win_raw[ df_win_raw.MENU_HINT.str.contains('AUS', na = False) ]
if DEBUG : print(df_win.shape) 
# 28,133 for 2021 DEC
# 322,471 for 2021

summ_win = hd.describe_df(df_win)

del df_win_raw

df_win.loc[ :, "EVENT_DT_FIX"] = df_win.EVENT_DT.str.replace('/','-')
#evntdt_qc = df_win[ df_win.EVENT_DT.str.contains('/') ][ ["EVENT_DT","EVENT_DT_FIX"] ]


#df_plc_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = False , check_for_word = '122021.', DEBUG = False)
df_plc_raw = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = True, check_for_word = '2021.', DEBUG = False)

if DEBUG : print(df_plc_raw.shape)
# 51,481 for 2021 DEC 
# 603,509 for 2021

summ_plc_raw = hd.describe_df(df_plc_raw)

df_plc = df_plc_raw[df_plc_raw.MENU_HINT.str.contains('AUS', na = False)]
if DEBUG : print(df_plc.shape)
# 27,565 for 2021 DEC
# 315,725 for 2021

summ_plc = hd.describe_df(df_plc)

df_plc.loc[ :, "EVENT_DT_FIX"] = df_plc.EVENT_DT.str.replace('/','-')

del df_plc_raw
#evntdt_qc = df_win[ df_win.EVENT_DT.str.contains('/') ][ ["EVENT_DT","EVENT_DT_FIX"] ]



if DEBUG:
    print(df_plc.shape)
    print(df_win.shape)

    # Checking for overlap between the EVENT IDs 
    events_win = set(df_win.EVENT_ID.unique())
    selection_win = set(df_win.SELECTION_ID.unique())
    print(len(events_win ))
    
    events_plc = set(df_plc.EVENT_ID.unique())
    selection_plc = set(df_plc.SELECTION_ID.unique())
    print(len(events_plc ))
    
    interse_events = events_win.intersection(events_plc)
    print(len(interse_events))
    
    interse_selection = events_win.intersection(selection_plc)
    print(len(interse_selection))



    # Details for Merge
    print(df_win.columns.values.tolist())
    print(df_plc.columns.values.tolist())

    print(df_win.shape)
    print(df_plc.shape)


df_bf_raw = pd.merge(df_win, df_plc, on = ['MENU_HINT', 'EVENT_DT_FIX', 'SELECTION_NAME'] , how = 'left', suffixes=('_WIN', '_PLC'))\
                .sort_values(by = ['EVENT_DT_FIX', 'MENU_HINT', 'SELECTION_NAME'])\
                    .drop(columns = {'EVENT_DT_WIN', 'EVENT_DT_PLC'})
                    
if DEBUG: print(df_bf_raw.shape)
# 322,471 for 2021 from 323473 - There is a nxn match

summ_df_bf_raw = hd.describe_df(df_bf_raw)




#df_bf_raw.EVENT_NAME_PLC.value_counts(dropna = False)


# --------- Adding Columns of Interst to BF Data --------- 

# Example 30-11-2021 09:37
#df_bf_raw['Event_Dt'] = pd.to_datetime(df_bf_raw['EVENT_DT'], infer_datetime_format = True ).dt.date
df_bf_raw['Event_Dt_a'] = pd.to_datetime(df_bf_raw['EVENT_DT_FIX'], format = '%d-%m-%Y %H:%M').dt.date


df_bf_raw.loc[:,"Box"] = df_bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[0].str.replace('.','')
df_bf_raw.loc[:,"Rug"] = df_bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[0].str.replace('.','')

df_bf_raw.loc[:,"DogName"] = df_bf_raw["SELECTION_NAME"].str.split(' ', 1, expand=True)[1].str.upper().replace(".","").replace("'","")

#qc_DogName_bf = df_bf.DogName.value_counts()

df_bf_raw[['country', 'race_track_details']] = df_bf_raw['MENU_HINT'].str.split('/', 1, expand = True )
df_bf_raw.loc[:,"country"] = df_bf_raw["country"].str.strip()

df_bf_raw[['Track', 'Event_Dt_MenuHint']] = df_bf_raw['race_track_details'].str.split('(', 1, expand = True )

df_bf_raw.loc[:,"Track"] = df_bf_raw["Track"].str.strip()

#df_bf_raw.loc[:,"Event_Dt_MenuHint"] = df_bf_raw["Event_Dt_MenuHint"].str.replace(r'\bAUS) \b','')
#df_bf_raw.loc[:,"Event_Dt_MenuHint_2"] = df_bf_raw["Event_Dt_MenuHint"].str.split(')', 1, expand = True)[1]


df_bf_raw.loc[:,"Day"]  = df_bf_raw.Event_Dt_MenuHint.str.extract(r'([0-9.]+)', expand = False).astype(int)
df_bf_raw.loc[:,"Year"]  = pd.to_datetime(df_bf_raw['Event_Dt_a']).dt.year
df_bf_raw.loc[:,"MonthName"]  = df_bf_raw.Event_Dt_MenuHint.str[-3:]
#df_bf_raw.loc[:,'Month'] = df_bf_raw['MonthName'].apply(lambda x: calendar.month_abbr[x])
df_bf_raw.loc[:,'Month'] = df_bf_raw['MonthName'].apply(lambda x: datetime.datetime.strptime(x, "%b").strftime("%m"))

df_bf_raw.loc[:,'Event_Dt'] = pd.to_datetime( df_bf_raw[['Year', 'Month', 'Day']]).dt.date



df_bf_raw.loc[df_bf_raw.Track.isin(['The Meadows']), "Track"] = 'Meadows'

summ_df_bf_raw = hd.describe_df(df_bf_raw)


'''

Check if any other kind of Boxes Available in the BF Data

    a) Just Crap Data
        df_bf_raw.Box.value_counts()
        temp = df_bf_raw[ ~df_bf_raw.Box.isin(['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])]
        
    b) Clear out races that have missing data for 'Place'
        
'''


missing_menus_df = df_bf_raw.groupby('MENU_HINT').agg({'EVENT_NAME_PLC': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'EVENT_NAME_PLC':'miss'})
missing_menus = missing_menus_df[missing_menus_df.miss > 0].MENU_HINT.values.tolist()

# Filtering for a) Australian b) Only GH in the races
df_bf = df_bf_raw[ df_bf_raw.Box.isin(['1','2','3','4','5','6','7','8']) \
                  & df_bf_raw.country.isin(['AUS']) \
                      & ~(df_bf_raw.MENU_HINT.isin(missing_menus))]

if DEBUG : print(df_bf.shape) 
# 24220 for 2021 DEC
# 270500 for 2021
    
df_bf.loc[:,"Box"] = df_bf["Box"].astype(float)

#df_bf_mg = df_bf[ df_bf.Rug.isin(['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']) & df_bf.country.isin(['AUS'])]
df_bf.loc[:,"Rug"] = df_bf["Rug"].astype(float)

summ_df_bf = hd.describe_df(df_bf)

print(len(df_bf_raw.MENU_HINT.unique().tolist()))
print(len(df_bf.MENU_HINT.unique().tolist()))
# Lost about 3,420 / 4,053 races in the process of cleaning it up approx 15% of the races


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

#res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\dog_results_20211201_20211231.csv')
res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\dog_results_20210101_20220424.csv')

res_raw.loc[:,"DogName"] = res_raw["DogName"].str.replace("'","").str.replace(".","")
if DEBUG: print(res_raw.shape) 
# 79,464


#if DEBUG: res_raw[ ~(res_raw.Place.isin( ['D','F','N','R','S','T',''])) ].shape # 66608
if DEBUG: print(res_raw[ ~(res_raw.Place.isin( ['R','S'])) ].shape) # 32,180

res_raw2 = res_raw[ ~(res_raw.Place.isin( ['R','S']))  ]
res_ = res_raw2[~res_raw2.Place.isna()]
if DEBUG: print(res_.shape) #65839

del res_raw, res_raw2

#res_ = res_raw

# Importing Race Details 
#race_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\race_details_20211201_20211231.csv', parse_dates = True)
race_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\race_details_20210101_20220424.csv', parse_dates = True)

race_raw['Event_Dt'] = pd.to_datetime(race_raw['date']).dt.date

dtvalct = race_raw.Event_Dt.value_counts()


race_raw.loc[race_raw.Track.isin(['Murray Bridge (MBR)','Murray Bridge (MBS)']), "Track"] = 'Murray Bridge'
race_raw.loc[race_raw.Track.isin(['Richmond (RIS)']), "Track"] = 'Richmond'

race_raw.loc[race_raw.Track.isin(['Sandown (SAP)']), "Track"] = 'Sandown Park'

race_raw.loc[race_raw.Track.isin(['Meadows (MEP)']), "Track"] = 'Meadows'
race_raw.loc[race_raw.Track.isin(['The Meadows']), "Track"] = 'Meadows'


if DEBUG : print(race_raw.shape)

race_ = race_raw[ ~race_raw.Track.str.contains('NZ')]
if DEBUG : print(race_.shape)

del race_raw

if DEBUG: print(race_.dtypes)

if DEBUG:
    print(res_.columns.values.tolist())
    print(race_.columns.values.tolist())
    
    print(res_.shape)
    print(race_.shape)

df_ft = pd.merge(res_, race_, left_on = 'RaceId', right_on = '@id', how = 'inner')
if DEBUG: print(df_ft.shape) #28,610

#qc_DogName = df_ft_merg.DogName.value_counts()

summ_ft = hd.describe_df(df_ft)



#----------------------------------------------------------------- Sets Track a) BF b) FT Data -----------------------------------------------------------------

ft_trk = df_ft.Track.unique()

ft_track = set(df_ft.Track.unique())
print(len(ft_track))

bf_trk = df_bf[ df_bf.country.isin(['AUS'])].Track.unique()

bf_track = set(df_bf[ df_bf.country.isin(['AUS'])].Track.unique())
print(len(bf_track))

inters = ft_track.intersection(bf_track)
print(len(inters))


#----------------------------------------------------------------- Merge a) BF b) FT Data -----------------------------------------------------------------

'Try on Race Date + GH Name (which includes the gate number & Uppercase all)'

# Looking at FastTrack Dataset
pd.crosstab(df_ft.Rug, df_ft.Box, dropna= False)

# Merging the Datasets

#df_ft.shape
#df_ft[ df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape



'''
FAILED : Merge Key ['Event_Dt','DogName', 'Rug']

print(df_bf[ df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape)

df_final_rug = pd.merge( df_bf[ df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ]\
                    , df_ft[ df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ]\
                        , on = ['Event_Dt','DogName', 'Rug'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT_WIN','EVENT_NAME_WIN','SELECTION_NAME'])
summ_df_final_rug = hd.describe_df(df_final_rug)
print(df_final_rug.shape)
'''


'''
MERGE KEY : ['Event_Dt','DogName', 'Box']

print(df_bf.shape)
print(df_bf.Event_Dt.value_counts())

print(df_bf[ df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ].shape) # 27,144

df_final_box = pd.merge( df_bf[ df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() & df_bf[ df_bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ]\
                    , df_ft[ df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() & df_ft['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ]\
                        , on = ['Event_Dt','DogName', 'Box'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])
summ_df_final_box = hd.describe_df(df_final_box)
# 6.12% Missing of 1,661 / 27,114 records

print(df_final_box.shape)
# 2560

'''


'''
TRY : Merge Key -> ['Event_Dt','DogName', 'Track']
'''

print(df_bf.shape) 
# 23,533

print(df_bf[ ( df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() )\
            & ( df_bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-31' , "%Y-%m-%d").date() ) \
                ].shape)
# 22,613

df_final_v3 = pd.merge( df_bf[ (df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & (df_bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-31' , "%Y-%m-%d").date() ) ]\
                    , df_ft[ (df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & ( df_ft['Event_Dt'] <= datetime.datetime.strptime('2021-12-31' , "%Y-%m-%d").date() )]\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(df_final_v3.shape) # 22,613 - NO nxn Match

summ_df_final_v3 = hd.describe_df(df_final_v3)
#0.07% MISMATCH, 18 / 22,613 records 



df_final_v3.groupby( [ 'Box_x' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})
df_final_v3.groupby( [ 'Event_Dt' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})
df_final_v3.groupby( [ 'Track' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

mh = df_final_v3.groupby( [ 'MENU_HINT' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

print(mh[mh.miss > 0].MENU_HINT.values.tolist())



df_final_v3_outer = pd.merge( df_bf[ (df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & (df_bf['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() ) ]\
                    , df_ft[ (df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-01' , "%Y-%m-%d").date() ) & ( df_ft['Event_Dt'] <= datetime.datetime.strptime('2021-12-30' , "%Y-%m-%d").date() )]\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'outer')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])


qc = df_final_v3_outer[df_final_v3_outer.Track.isin(['Richmond'])]

qc = df_final_v3_outer[df_final_v3_outer.MENU_HINT.isin( mh[mh.miss > 0].MENU_HINT.values.tolist() )]


print(df_final_v3.Track.unique().tolist())

df_final_v3.Place.value_counts()




'''
find out duplicates and a logic to delete the redundant ones
    which is the correct box - the ones assigned with a number or a letter

'''



#
qc = df_final[df_final.isna()]

df_final.Event_Dt.value_counts(dropna = False)



od_bf = df_bf[ df_bf['Event_Dt'] >= datetime.datetime.strptime('2021-12-15' , "%Y-%m-%d").date() ]

od_ft = df_ft[ df_ft['Event_Dt'] >= datetime.datetime.strptime('2021-12-15' , "%Y-%m-%d").date() ]


x1 = od_bf.Track.value_counts()
x2 = od_ft.Track.value_counts()

od_qc_left = pd.merge( od_bf \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'left')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_left.shape) # 388 FT Nans from 12456 rows, a missmath % of 3.115
summ_df_od_qc_left = hd.describe_df(od_qc_left)


od_qc_left.groupby( [ 'Box_x' ] ).agg({'Box_y': lambda x: x.isnull().sum()}).reset_index().rename(columns = {'Box_y':'miss'})

pd.crosstab(od_qc_left.Box_x, od_qc_left.Box_y, dropna = False)

print(od_qc_left.Box_x.value_counts())

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


od_qc_righ = pd.merge( od_bf_mg \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Box'] , how = 'right')\
                            .sort_values(by = ['MENU_HINT_WIN','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_righ.shape) # 958 rows , 217 Na
summ_df_od_qc_righ = hd.describe_df(od_qc_righ)

del od_qc_outer
del summ_df_od_qc_oute 

print(od_bf.Track.unique().tolist())
print(od_ft.Track.unique().tolist())


print(od_bf.columns.values.tolist())
print(od_ft.columns.values.tolist())

od_qc_outer = pd.merge( od_bf \
                    , od_ft\
                        , on = ['Event_Dt','DogName', 'Track'] , how = 'outer')\
                            .sort_values(by = ['MENU_HINT','EVENT_NAME_WIN','SELECTION_NAME'])

print(od_qc_outer.shape) # 1264,
summ_df_od_qc_oute = hd.describe_df(od_qc_outer)






print(od_main_mg.Event_Dt.value_counts())

print(df_ft_merg.Event_Dt.value_counts())
print(df_ft_merg.EVENT_DT.value_counts())

#----------------------------------------------------------------- EXPLORATORY DATA ANALYSIS -----------------------------------------------------------------

#----------------------------------------------------------------- Adding Columns -----------------------------------------------------------------

if DEBUG: print(res_.shape)

res_.loc[:,"pos"] = res_.apply( lambda x: x['Place'].replace('=',''), axis = 1 )
res_.loc[:,"pos"] = res_["pos"].astype(int)


res_.loc[:,"flag_fav"] = res_["StartPrice"].apply(lambda x : np.nan if pd.isna(x) else True if 'F' in x else False )
res_.loc[:,"flag_fav"] = res_["flag_fav"].astype(bool)

res_.loc[:,"StartPrice"] = res_["StartPrice"].astype(str)
res_.loc[:,"sp"] = res_.apply( lambda x: np.nan if pd.isna(x.flag_fav) else x["StartPrice"].replace('F','').replace('$','') if x.flag_fav  else x["StartPrice"].replace('$','') , axis = 1 )
res_.loc[:,"sp"] = res_['sp'].astype(float)

res_.loc[:,"rank_"] = res_.groupby( ['RaceId'] )['sp'].rank("dense", ascending=True)

res_.loc[:,"flag_top1"] = res_.apply(lambda x : np.nan if pd.isna(x.rank_) else True if x.rank_ <= 1 else False, axis = 1)
res_.loc[:,'flag_top2'] = res_.apply(lambda x : np.nan if pd.isna(x.rank_) else True if x.rank_ <= 2 else False, axis = 1)
res_.loc[:,'flag_top3'] = res_.apply(lambda x : np.nan if pd.isna(x.rank_) else True if x.rank_ <= 3 else False, axis = 1)

res_.loc[:,'flag_win'] = res_.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 1 else False, axis = 1)
res_.loc[:,'flag_win'] = res_['flag_win'].astype(bool)

res_.loc[:,'flag_top2'] = res_.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 2 else False, axis = 1)
res_.loc[:,'flag_top2'] = res_['flag_top2'].astype(bool)

res_.loc[:,"flag_plc"] = res_.apply(lambda x : np.nan if pd.isna(x.pos) else True if x.pos <= 3 else False, axis = 1)
res_.loc[:,"flag_plc"] = res_["flag_plc"].astype(bool)


#----------------------------------------------------------------- Strategy Flags -----------------------------------------------------------------


'''

s1 - Strategy 1 (Favourite based strategies)
    1 Fav to win aka bet a $1 o the favourite    
        1 fav to win under/over 1.5
        2 fav to win under/over 2.0
        3 fav to win under/over 2.5
        4 fav to win under/over 3.0

    2 Fav to Place

s2 - Strategy 2 (Top 3 Based Strategies )
    1 All top 3 to place 
    2 Any of the top 3 to win 
        bet on top 2 to win
        bet on top 3 to win, is that 

'''

#res_.loc[:,"s1_1"] = res_.apply(lambda x : (x.flag_fav) & (x.flag_win), axis = 1 )
res_.loc[:,"s1_1"] = ( res_.flag_fav )

res_.loc[:,"s1_11"] = ( res_.flag_fav ) & ( res_.sp <= 1.5)
res_.loc[:,"s1_12"] = ( res_.flag_fav ) & ( res_.sp <= 2.0)
res_.loc[:,"s1_13"] = ( res_.flag_fav ) & ( res_.sp <= 2.5)
res_.loc[:,"s1_14"] = ( res_.flag_fav ) & ( res_.sp <= 3.0)



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

strategies = ['1_1', '1_11', '1_12', '1_13']

finalres = pd.DataFrame( columns = ['strategy','races','profit','profitability'] )

for strat in strategies:
    res_.loc[:,'p'+ strat] = res_.apply(lambda x : x.sp - 1 if ( x['s'+strat] == x['flag_win'] ) & (x['s'+strat])\
                                        else -1 if ~( x['s'+strat] == x['flag_win'] ) & (x['s'+strat]) \
                                            else 0
                                    , axis=1)

    # Adding the Necessary cols
    races = res_['s'+strat].sum()
    profit = res_['p'+strat].sum()
    profitability = round(float(profit/ races)*100,1)
    
    row_input = [strat, races, profit, str(profitability) + '%' ]
    
    finalres.loc[len(finalres)] = row_input
    




#----------------------------------------------------------------- Planning and Plotting  -----------------------------------------------------------------


res_.Place.value_counts(dropna=False)

temp = res_[res_.Place.isna()]
 
print(res_.shape)

eda1 = res_.groupby(['Place','flag_fav'], dropna= False).agg({'@id':'count'}, dropna = False).unstack(level=1)

res_.sp.plot(kind = 'hist', bins = 50)

res_['Place'].value_counts()

res_['flag_top3'] = res_.apply( lambda x: True if x.Place <=3 else False , axis = 1 )





#----------------------------------------------------------------- EXPLORATORY DATA ANALYSIS -----------------------------------------------------------------

summ_res = hd.describe_df(res_)


