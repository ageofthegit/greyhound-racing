# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd, numpy as np

import helpdesk as hd


DEBUG = True

#----------------------------------------------------------------- DATA IMPORT -----------------------------------------------------------------

#----------------------------------------------------------------- Betfair Data -----------------------------------------------------------------


df_win = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win', drop_dups = False , check_for_word = '122021.', DEBUG = False)
summ_win = hd.describe_df(df_win)

df_plc = hd.import_all_csvfiles_into_df(path= 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place', drop_dups = False , check_for_word = '122021.', DEBUG = False)
summ_plc = hd.describe_df(df_plc)

if DEBUG:
    print(df_plc.shape)
    print(df_win.shape)


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


print(df_win.columns.values.tolist())
print(df_plc.columns.values.tolist())


print(df_win.shape)
print(df_plc.shape)

df_main = pd.merge( df_win, df_plc, on = ['EVENT_DT', 'SELECTION_NAME'] , how = 'left', suffixes=('_WIN', '_PLC'))
print(df_main.shape)

summ_main = hd.describe_df(df_main)

temp_win = df_win[df_win.EVENT_ID.isin([192053304])]
temp_plc = df_win[df_win.EVENT_ID.isin([192053305])]



#----------------------------------------------------------------- Fast Track Data -----------------------------------------------------------------

res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\dog_results_20210101_20220424.csv')

if DEBUG: print(res_raw.shape) #79464
if DEBUG: res_raw[ ~(res_raw.Place.isin( ['D','F','N','R','S','T',''])) ].shape # 66608

res_raw2 = res_raw[ ~(res_raw.Place.isin( ['D','F','N','R','S','T',''])) ]
res_ = res_raw2[~res_raw2.Place.isna()]
if DEBUG: print(res_.shape) #65839

#del res_raw, res_raw2

race_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\race_details_20210101_20220424.csv')

if DEBUG: print(race_raw.shape) #8,949


print(res_raw.columns.values.tolist())
print(race_raw.columns.values.tolist())

print(res_raw.shape)
print(race_raw.shape)

df_ft_merg = pd.merge(res_raw, race_raw, left_on = 'RaceId', right_on = '@id', how = 'left')

print(df_ft_merg.shape)

summ_ft_merg = hd.describe_df(df_ft_merg)



#----------------------------------------------------------------- Merge a) BF b) FT Data -----------------------------------------------------------------


'Try on Race Date + GH Name (which includes the gate number & Uppercase all)'

pd.merge(df_main, res_raw)



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


