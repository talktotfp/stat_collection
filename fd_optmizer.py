# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 15:26:03 2017

@author: tpauley
"""

import pymysql
import pandas as pd
import cx_Oracle 
from ortools.algorithms import pywrapknapsack_solver as pysolver
from pulp import *
import random
from datetime import datetime


def create_lineup(idf):
   "This prints a passed string into this function"
   pos1 = idf[idf['PG'] == 1]  
   pos2 = idf[idf['SG'] == 1]  
   pos3 = idf[idf['SF'] == 1]  
   pos4 = idf[idf['PF'] == 1]  
   pos5 = idf[idf['C'] == 1]  
   frames = [pos1.sample(n=2),pos2.sample(n=2),pos3.sample(n=2),pos4.sample(n=2),pos5.sample(n=1)]
   lineup = pd.concat(frames)
   df = pd.DataFrame(columns=('PG', 'PG2', 'SG','SG2','SF','SF2','PF','PF2','C','COST','SCORE'))
   df.loc[0] = [lineup['NAME'].iloc[0],
        lineup['NAME'].iloc[1],
        lineup['NAME'].iloc[2],
        lineup['NAME'].iloc[3],
        lineup['NAME'].iloc[4],
        lineup['NAME'].iloc[5],
        lineup['NAME'].iloc[6],
        lineup['NAME'].iloc[7],
        lineup['NAME'].iloc[8],
        cost_lineup(lineup),
        score_lineup(lineup)]
   return df
   
   
   
   
def score_lineup(lineup):
    return lineup['POINTS'].sum()
 
def cost_lineup(lineup):
    return lineup['SAL'].sum()
    
def mix_lineups(lineup1, lineup2):
    mix = pd.concat([lineup1,lineup2])
    mix_lineup = pd.concat([idf.loc[mix['PG']],idf.loc[mix['PG2']],idf.loc[mix['SG']],idf.loc[mix['SG2']],
                idf.loc[mix['SF']],idf.loc[mix['SF2']],idf.loc[mix['PF']],idf.loc[mix['PF2']],
                idf.loc[mix['C']]])
#    mix_pg = mix_pg[~mix_pg.index.duplicated(keep='first')]
    return create_lineup(mix_lineup)
    
def unmix(idf, mix):
    mix_lineup = pd.concat([idf.loc[mix['PG']],idf.loc[mix['PG2']],idf.loc[mix['SG']],idf.loc[mix['SG2']],
                idf.loc[mix['SF']],idf.loc[mix['SF2']],idf.loc[mix['PF']],idf.loc[mix['PF2']],
                idf.loc[mix['C']]])
#    mix_pg = mix_pg[~mix_pg.index.duplicated(keep='first')]
    return mix_lineup[~mix_lineup.index.duplicated(keep='first')]
    
def make_topmix(first_cut,idf):
    for x in range (0,1000):
        loop_lineup = create_lineup(idf)
        if loop_lineup['COST'].iloc[0] <=60000 and loop_lineup['SCORE'].iloc[0] >200:
            first_cut = pd.concat([first_cut,loop_lineup])
        if len(first_cut) >= 10:
            break
    first_cut = first_cut.sort_values(['SCORE'], ascending=False)
    top1 = first_cut.iloc[0]
    top2 = first_cut.iloc[1]
    top3 = first_cut.iloc[3]
    top4 = first_cut.iloc[4]
    top5 = first_cut.iloc[5]
    return pd.concat([mix_lineups(top1,top2),mix_lineups(top1,top3),mix_lineups(top1,top4),
                         mix_lineups(top1,top5),mix_lineups(top2,top3),mix_lineups(top2,top4),
                         mix_lineups(top2,top5),mix_lineups(top3,top4),mix_lineups(top3,top5),
                         mix_lineups(top4,top5),create_lineup(idf),create_lineup(idf),create_lineup(idf)]).sort_values(['SCORE'], ascending=False)

     
oracle_con = cx_Oracle.connect('tylerp/tp323ean@ukudbsh1/ukm25d')
oracle_cur = oracle_con.cursor()
oracle_query = """select name as PLAYER_ID, NAME, SAL, ADJ_MOD1_PROJ as POINTS,
CASE WHEN POS = 'PG' then 1 else 0 end as PG,
CASE WHEN POS = 'SG' then 1 else 0 end as SG,
CASE WHEN POS = 'SF' then 1 else 0 end as SF,
CASE WHEN POS = 'PF' then 1 else 0 end as PF,
CASE WHEN POS = 'C' then 1 else 0 end as C
from HIST_LINEUP_PROJ_FD
where gdate = trunc(sysdate)-1"""

df = pd.read_sql_query(oracle_query,oracle_con)

idf = df.set_index('PLAYER_ID')


startTime = datetime.now()
first_cut = create_lineup(idf)
results = first_cut
new_list = pd.DataFrame()
for x in ['PG','PG2','SG','SG2','SF','SF2','PF','PF2','C']:
    player = results[x]
    sal = float(idf['SAL'].loc[player])
    leftover = 60000 - results['COST'] - sal
    pos_idf = idf[(idf[x.replace('2','')] == 1) ]
    pos_top = pos_idf[pos_idf['SAL'] < int(leftover)].sort_values(['POINTS'], ascending=False).iloc[0]
    if x == 'PG':
        max_top = pos_top
    if pos_top['POINTS'] > max_top['POINTS']:
        max_top = pos_top
    print(pos_top)
#    print(pos_idf[pos_idf['SAL'] < int(leftover)].sort_values(['POINTS'], ascending=False).iloc[0])
print(max_top) 
#  final_cut[['SCORE']].max(axis=1))  
    

#startTime = datetime.now()

#for y in range(0,4):
#    for x in range(0,25):
#        
#        mixer = make_topmix(first_cut,idf)
#        first_cut = mixer
#        results = pd.concat([results,first_cut])
#    results = results[results['SCORE'] >225].sort_values(['SCORE'], ascending=False)
#
#print(results[results['COST'] <= 60000].sort_values(['SCORE'], ascending=False).drop_duplicates(keep=False))
#print (datetime.now() - startTime )   
#result_set =  results[results['COST'] <= 60000].sort_values(['SCORE'], ascending=False).drop_duplicates(keep=False)      

             
#oracle_cur.execute('truncate table daily_lineups')
#for index in range(0, len(result_set)):
#
#    insert_query = '''insert into daily_lineups
#       values (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)'''
#       
#    val1 =str(result_set.iloc[index]['PG'])
#    val2 =str(result_set.iloc[index]['PG2'])
#    val3 =str(result_set.iloc[index]['SG'])
#    val4 =str(result_set.iloc[index]['SG2'])
#    val5 =str(result_set.iloc[index]['SF'])
#    val6 =str(result_set.iloc[index]['SF2'])
#    val7 =str(result_set.iloc[index]['PF'])
#    val8 =str(result_set.iloc[index]['PF2'])
#    val9 =str(result_set.iloc[index]['C'])
#    val10 =str(result_set.iloc[index]['SCORE'])
#    val11 =str(result_set.iloc[index]['COST'])
#    oracle_cur.execute(insert_query,
#                 (val1,val2,val3,val4,val5,
#                  val6,val7,val8,val9,val10,val11))
#    oracle_con.commit()
oracle_cur.close()
oracle_con.close()


##second_cut = first_cut.iloc[:3]
#final_cut= create_lineup(idf)
#print(final_cut[['SCORE']].max(axis=1))
#for x in range (0,10):
#    
#    for x in range (0,1000):
#        loop_lineup = create_lineup(idf)
#        if loop_lineup['COST'].iloc[0] <=60000 and loop_lineup['SCORE'].iloc[0] >175:
#            first_cut = pd.concat([first_cut,loop_lineup])
#        if len(first_cut) >= 10:
#            break
#    first_cut = first_cut.sort_values(['SCORE'], ascending=False)
#    top1 = first_cut.iloc[0]
#    top2 = first_cut.iloc[1]
#    top3 = first_cut.iloc[3]
#    top4 = first_cut.iloc[4]
#    top5 = first_cut.iloc[5]
#    top_mix = pd.concat([mix_lineups(top1,top2),mix_lineups(top1,top3),mix_lineups(top1,top4),
#                         mix_lineups(top1,top5),mix_lineups(top2,top3),mix_lineups(top2,top4),
#                         mix_lineups(top2,top5),mix_lineups(top3,top4),mix_lineups(top3,top5),
#                         mix_lineups(top4,top5),create_lineup(idf),create_lineup(idf),create_lineup(idf)])
#
#     
#    loop2_lineup = create_lineup(unmix(idf,top_mix))
#    if loop2_lineup['COST'].iloc[0] <=60000:
#        second_cut = pd.concat([second_cut,loop2_lineup])
#    first_cut =  second_cut.sort_values(['SCORE'], ascending=False).iloc[:5]
#
#    for i in range(0,10):
#        if second_cut['SCORE'].iloc[i] > 250:
#            final_cut = pd.concat([final_cut,second_cut.iloc[i]])
#    
#print(final_cut.sort_values(['SCORE'], ascending=False))
#print (datetime.now() - startTime )


#
#
#
#
#startTime = datetime.now()
#first_cut = create_lineup(pg,sg,sf,pf,c)
##first_cut['cost'] = cost_lineup(first_cut)
##first_cut['total'] = score_lineup(first_cut)
###x = 0
#for x in range(0,1000):
#   lineup = create_lineup(pg,sg,sf,pf,c)
#
#   first_cut = pd.concat([first_cut,lineup])
#   if len(first_cut) >= 90:
#       break
#print(first_cut)
#
#
#for x in range(0,1000):
#   lineup = create_lineup(pg,sg,sf,pf,c)
#
#   if cost_lineup(lineup) <= 60000:
#          lineup['total'] = score_lineup(lineup)
#          lineup['cost'] = cost_lineup(lineup)
#          first_cut = pd.concat([first_cut,lineup])
#   if len(first_cut) >= 90:
#       break
#print(first_cut)
#
#def mix_rank(first_cut):
#    for x in range(1,3):
#        for y in range (1,3):
#            z = x*9
#            u = y*9
#            top_mix1 = mix_lineups(first_cut.sort_values(['total'],ascending=False).iloc[:z],first_cut.sort_values(['total'],ascending=False).iloc[:u]).drop('total', 1).drop('cost', 1)
#            top_mix1['total'] = score_lineup(top_mix1)
#            top_mix1['cost'] = cost_lineup(top_mix1)
#            return pd.concat([top_mix1,second_cut,create_lineup(pg,sg,sf,pf,c)])
#            
#for z in range(1,100):
#    y = mix_rank(first_cut)
#    
#
#print(valid_second_cut[valid_second_cut.cost <= 60000])    
#print (datetime.now() - startTime )


