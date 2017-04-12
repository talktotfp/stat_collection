# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:08:02 2017

@author: tpauley
"""
#set number of lineups to generate
num_lineups = 10

#set point difference in lineups
point_gap = .01

import pulp
import cx_Oracle 
import pandas as pd
from tabulate import tabulate
import timeit
import matplotlib.pyplot as plt
import numpy as np
import datetime
#function for cleaning name strings in optimized results
def clean_result_strings(string):
    for ch in ['c_','pf_','sf_','sg_','pg_']:
        if ch in string:
            string=string.replace(ch,'')
    return string.replace('_',' ').replace('margasol','marc gasol')

#open oracle connection
ip = 'localhost'
port = 1522
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)

oracle_con = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
#oracle_con = cx_Oracle.connect('nba/rp4490@localhost/xe')
oracle_cur = oracle_con.cursor()

#sql to select daily lineups and projections
oracle_query = """select replace(name,'-',' ') as PLAYER_ID, PLAYER_ID as NUM_ID, NAME as NAME, DFS_STD_DEV, SAL, ROUND(ADJ_MOD1_PROJ,3) as POINTS,
CASE WHEN POS = 'PG' then 1 else 0 end as PG,
CASE WHEN POS = 'SG' then 1 else 0 end as SG,
CASE WHEN POS = 'SF' then 1 else 0 end as SF,
CASE WHEN POS = 'PF' then 1 else 0 end as PF,
CASE WHEN POS = 'C' then 1 else 0 end as C,
ADJ_MOD1_PCT_DIFF,ADJ_MOD1_REAL_DIFF
from HIST_LINEUP_PROJ_FD
where gdate = trunc(sysdate)"""

#load in query as dataframe
df = pd.read_sql_query(oracle_query,oracle_con)

#index the dataframe by player name 
idf = df.set_index('PLAYER_ID')



#convert positions to individual lists
pg = idf[idf['PG'] == 1]['NAME'].tolist()
sg = idf[idf['SG'] == 1]['NAME'].tolist()
sf = idf[idf['SF'] == 1]['NAME'].tolist()
pf = idf[idf['PF'] == 1]['NAME'].tolist()
c = idf[idf['C'] == 1]['NAME'].tolist()

#create dictionary of point projections for each position
pg_pts = dict( zip( pg, idf[idf['PG'] == 1]['POINTS'].tolist()) )
sg_pts = dict( zip( sg, idf[idf['SG'] == 1]['POINTS'].tolist()) )
sf_pts = dict( zip( sf, idf[idf['SF'] == 1]['POINTS'].tolist()) )
pf_pts = dict( zip( pf, idf[idf['PF'] == 1]['POINTS'].tolist()) )
c_pts = dict( zip( c, idf[idf['C'] == 1]['POINTS'].tolist()) )

#repeat above with salary dictionary
pg_sal = dict( zip( pg, idf[idf['PG'] == 1]['SAL'].tolist()) )
sg_sal = dict( zip( sg, idf[idf['SG'] == 1]['SAL'].tolist()) )
sf_sal = dict( zip( sf, idf[idf['SF'] == 1]['SAL'].tolist()) )
pf_sal = dict( zip( pf, idf[idf['PF'] == 1]['SAL'].tolist()) )
c_sal = dict( zip( c, idf[idf['C'] == 1]['SAL'].tolist()) )





#set position variables for solver
lpg     = pulp.LpVariable.dicts( "pg", indexs = pg, lowBound=0, upBound=1, cat='Integer', indexStart=[] )
lsg     = pulp.LpVariable.dicts( "sg", indexs = sg, lowBound=0, upBound=1, cat='Integer', indexStart=[] )
lsf     = pulp.LpVariable.dicts( "sf", indexs = sf, lowBound=0, upBound=1, cat='Integer', indexStart=[] )
lpf     = pulp.LpVariable.dicts( "pf", indexs = pf, lowBound=0, upBound=1, cat='Integer', indexStart=[] )
lc     = pulp.LpVariable.dicts( "c", indexs = c, lowBound=0, upBound=1, cat='Integer', indexStart=[] )



#setup to spit out multiple lineups
max_val = 1000
start = timeit.default_timer()
lineup_res = pd.DataFrame([])
export_res = pd.DataFrame([])
overall_res = pd.DataFrame([])
for i in range(0,num_lineups):
    #setup solver objective (sum of all points per player)
    prob  = pulp.LpProblem( "Minimalist example", pulp.LpMaximize )
    prob += pulp.lpSum( [ lpg[i]*pg_pts[i] for i in pg ] + 
                       [ lsg[i]*sg_pts[i] for i in sg ] +
                       [ lsf[i]*sf_pts[i] for i in sf ] +
                       [ lpf[i]*pf_pts[i] for i in pf ] +
                       [ lc[i]*c_pts[i] for i in c ]), " Objective of total points "
    
    #setup constraints for solver
    prob += pulp.lpSum( [ lpg[i]*pg_sal[i] for i in pg ] + 
                       [ lsg[i]*sg_sal[i] for i in sg ] +
                       [ lsf[i]*sf_sal[i] for i in sf ] +
                       [ lpf[i]*pf_sal[i] for i in pf ] +
                       [ lc[i]*c_sal[i] for i in c ]) <= 60000, " Constraint of total salary "
    prob += pulp.lpSum( [ lpg[i] for i in pg ] )==2, " Constraints for number of players"
    prob += pulp.lpSum( [ lsg[i] for i in sg ] )==2
    prob += pulp.lpSum( [ lsf[i] for i in sf ] )==2
    prob += pulp.lpSum( [ lpf[i] for i in pf ] )==2
    prob += pulp.lpSum( [ lc[i] for i in c ] )==1, " Constraint is that we choose two items "
    
    prob += pulp.lpSum( [ lpg[i]*pg_pts[i] for i in pg ] + 
                       [ lsg[i]*sg_pts[i] for i in sg ] +
                       [ lsf[i]*sf_pts[i] for i in sf ] +
                       [ lpf[i]*pf_pts[i] for i in pf ] +
                       [ lc[i]*c_pts[i] for i in c ]) <= max_val - point_gap
    
    #run solver
    prob.solve()

    
    
    
    #generate list of results from solver and clean names to match dataframe index (idf)        
    results = []
    for v in prob.variables():
        if v.varValue ==1:
            #results.append(v.name)
            results.append(clean_result_strings(v.name))
    
            
            
    #build dataframe of results
    results_df = idf.ix[results][['SAL','POINTS','NUM_ID']].sort_values(['POINTS'], ascending=False)
    #print solver results from idf dataframe
#    print(tabulate(results_df, headers='keys', tablefmt='psql'))
#    print('   ')
#    print ('Total Points', pulp.value(prob.objective))
#    print ('Total Cost', int(idf.ix[results][['SAL']].sum().values))
#    print ('Total Standard Deviation', int(idf.ix[results][['DFS_STD_DEV']].sum().values))
    max_val = pulp.value(prob.objective)
#    for x in range(0,9):
#        print(results_df.index[x])
    res_list = results_df.index
    
#    res_list = res_list.append([pulp.value(prob.objective)])
    lineup_res = pd.DataFrame(res_list).reset_index()
    lineup_res = lineup_res.transpose().ix[['PLAYER_ID']]
    lineup_res['lineup_id'] = i
    lineup_res['lineup_pts'] = pulp.value(prob.objective)
    lineup_res['lineup_cost'] = int(idf.ix[results][['SAL']].sum().values)
    lineup_res['lineup_dev'] = int(idf.ix[results][['DFS_STD_DEV']].sum().values)
    lineup_res['lineup_acc'] = int(idf.ix[results][['ADJ_MOD1_REAL_DIFF']].sum().values)*-1
    overall_res = pd.concat([overall_res,lineup_res])
    exp_temp = pd.DataFrame(idf['NUM_ID'].ix[res_list])
    exp_temp['lineup_id'] = i
    export_res = pd.concat([export_res,exp_temp])
    
overall_res = overall_res.reset_index()
stop = timeit.default_timer()   


overall_res['lineup_pts'] =  round(overall_res['lineup_pts'],2)
x = overall_res['lineup_pts']
y = overall_res['lineup_cost']
s = overall_res['lineup_dev']
ms = overall_res['lineup_acc']+10
color = '#ff6666'
n = overall_res['lineup_id']




#oracle_cur.execute("delete from OPT_LINEUPS_RAW where GDATE = trunc(sysdate)")
#for index, row in export_res.iterrows():
#    oracle_cur.execute("insert into OPT_LINEUPS_RAW (PLAYER_ID, LINEUP_ID, GDATE) select :1,:2, trunc(sysdate) from dual",
             #        (int(row['NUM_ID']),int(row['lineup_id'])))



overall_res.columns = ['index', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'lineup_id', 'lineup_pts', 'lineup_cost', 'lineup_dev', 'lineup_acc']
overall_res
overall_res['labels'] = pd.DataFrame("Total Points: " + overall_res["lineup_pts"].map(str)+ "</br>Model Accuracy: " + overall_res["lineup_acc"].map(str)  + "</br>Deviation: " + overall_res["lineup_dev"].map(str) + "</br></br>" + overall_res["p1"].map(str) + "</br>" + overall_res["p2"].map(str) + "</br>" + overall_res["p3"].map(str) + "</br>" + overall_res["p4"].map(str) + "</br>"
                      + overall_res["p5"].map(str) + "</br>" + overall_res["p6"].map(str) + "</br>" + overall_res["p7"].map(str) + "</br>" + overall_res["p8"].map(str) + "</br>"
                      + overall_res["p9"].map(str) + "</br></br>Lineup ID:" + overall_res["lineup_id"].map(str))

overall_res['labels']
lables = overall_res[['labels']]



import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import datetime
plotly.tools.set_credentials_file(username='pauley.45', api_key='OsbQXNQdXZlQhQVMfJOo')
text = overall_res['labels']


trace0 = go.Scatter(
    x= x,
    y=y,
    mode='markers',
    text=text,
    textposition='top',
    textfont=dict(
        family='sans serif',
        size=5
    ),
    marker=dict(
        #size=ms,
        size = 10,
        opacity= 0.55,
        line = dict(
            width = 1.5,
        ),
        color = s,
        colorscale = 'Portland',
        colorbar=ColorBar(
                title='Std Dev'
            ),
        
    )
)

layout = go.Layout(
    title= 'NBA Daily Fantasy Optimized Lineups (100 Lineups - Fanduel)',
    xaxis=dict(
        title='Projected Points'
    ),
    yaxis=dict(
        title='Total Salary',
        range = [59630,60050]
    )
)


data = [trace0]
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='bubblechart-text')



import plotly.figure_factory as FF


table = FF.create_table(overall_res[['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'lineup_id', 'lineup_pts', 'lineup_cost', 'lineup_dev']])

# Make text size larger
for i in range(len(table.layout.annotations)):
    table.layout.annotations[i].font.size = 8

py.iplot(table, filename='lineup results')
overall_res.to_csv('output.csv', sep=',')


oracle_cur.execute("delete from LINEUP_OUT_FD where GDATE = trunc(sysdate)")
for index, row in overall_res.iterrows():
    oracle_cur.execute("insert into LINEUP_OUT_FD (P1, P2, P3,P4,P5,P6,P7,P8,P9,LINEUP_ID,LINEUP_COST,LINEUP_PTS,LINEUP_DEV,LINEUP_ACC, GDATE) select :1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14, trunc(sysdate) from dual",
                     (str(row['p1']),
                      str(row['p2']),
                      str(row['p3']),
                      str(row['p4']),
                      str(row['p5']),
                      str(row['p6']),
                      str(row['p7']),
                      str(row['p8']),
                      str(row['p9']),
                      int(row['lineup_id']),
                      float(row['lineup_cost']),
                      float(row['lineup_pts']),
                      float(row['lineup_dev']),
                      float(row['lineup_acc'])))

#close oracle connection
oracle_con.commit()  
oracle_cur.close()
oracle_con.close()