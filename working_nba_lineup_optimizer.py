import pulp
import cx_Oracle 
import pandas as pd


#function for cleaning name strings in optimized results
def clean_result_strings(string):
    for ch in ['c_','pf_','sf_','sg_','pg_']:
        if ch in string:
            string=string.replace(ch,'')
    return string.replace('_',' ')

#open oracle connection
oracle_con = cx_Oracle.connect('tylerp/tp323ean@ukudbsh1/ukm25d')
oracle_cur = oracle_con.cursor()

#sql to select daily lineups and projections
oracle_query = """select replace(name,'-',' ') as PLAYER_ID, replace(NAME,'-',' ') as NAME, DFS_STD_DEV, SAL, ROUND(ADJ_MOD1_PROJ,3) as POINTS,
CASE WHEN POS = 'PG' then 1 else 0 end as PG,
CASE WHEN POS = 'SG' then 1 else 0 end as SG,
CASE WHEN POS = 'SF' then 1 else 0 end as SF,
CASE WHEN POS = 'PF' then 1 else 0 end as PF,
CASE WHEN POS = 'C' then 1 else 0 end as C
from HIST_LINEUP_PROJ_FD
where gdate = trunc(sysdate)-4"""

#load in query as dataframe
df = pd.read_sql_query(oracle_query,oracle_con)

#index the dataframe by player name 
idf = df.set_index('PLAYER_ID')

#close oracle connection
oracle_cur.close()
oracle_con.close()


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

#run solver
prob.solve()
print ("Status:", pulp.LpStatus[ prob.status ])

#generate list of results from solver and clean names to match dataframe index (idf)        
results = []
for v in prob.variables():
    if v.varValue ==1:
        results.append(clean_result_strings(v.name))


#print solver results from idf dataframe
print(idf.ix[results][['SAL','POINTS']].sort_values(['POINTS'], ascending=False))
print('   ')
print ('Total Points', pulp.value(prob.objective))
print ('Total Cost', int(idf.ix[results][['SAL']].sum().values))
