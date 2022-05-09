# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd, numpy as np

import helpdesk as hd


DEBUG = True

res_raw = pd.read_csv('C:\\Users\\karan\\Documents\\Data\\racing\\dog_results_20210101_20220424.csv')

if DEBUG: print(res_raw.shape) #79464
if DEBUG: res_raw[ ~(res_raw.Place.isin(['D','F','N','R','S','T',''])) ].shape # 66608

res_raw2 = res_raw[ ~(res_raw.Place.isin(['D','F','N','R','S','T',''])) ]
res_ = res_raw2[~res_raw2.Place.isna()]
if DEBUG: print(res_.shape) #65839

#del res_raw, res_raw2

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


