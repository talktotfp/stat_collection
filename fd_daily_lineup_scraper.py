# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:03:19 2016

@author: tpauley
"""

import requests
import bs4
import numpy as np
import pandas as pd
import datetime
import pymysql
import cx_Oracle

#oracle_con = cx_Oracle.connect('tylerp/tp323ean@ukudbsh1/ukm25d')
#oracle_query = "select * from PGAME_STAT_BASE where PLAYER_ID < 2000 and PLAYER_ID >1000"
#oracle_df = pd.read_sql_query(oracle_query,oracle_con)
#print(oracle_df)
#print (oracle_df.corr('pearson'))
#oracle_con.close()
ip = 'localhost'
port = 1522
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)


#connect to MySQL database
conn = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
#create connection cursor
cur = conn.cursor()


#get text from HTML document as response
response = requests.get('http://www.rotowire.com/daily/NBA/optimizer.php?site=FanDuel')

#setup BeaufifulSoup 
soup = bs4.BeautifulSoup(response.text,"lxml")


#find table in HTML by looking for 'tr' table row objects
table_body = soup.find_all('tr')

#build blank lists to be filled in
l_names = []
l_tm = []
l_opp = []
l_pos = []
l_sal = []
l_mins = []
l_pts = []
date = datetime.datetime.today().strftime("%m_%d_%Y")

#loop through all rows in HTML (table_body find all 'td')
for rows in table_body[2:]:
    col = rows.find_all('td')
    
    #find name and replace GTD and special characters
    nm = col[1].text.strip().replace("\nGTD", "").lower().replace(".","")
    tm = col[2].text.strip()
    opp = col[3].text.strip()
    pos = col[4].text.strip()
    
    #find mins, salary, and points and convert to floats
    mins = float(col[9].text.strip().replace(",", ""))
    sal = float(col[10].attrs.get("data-salary").replace(",", ""))
    pts = float(col[11].attrs.get("data-points").replace(",", ""))
    
    #append each of the columns to their respective lists
    l_names.append(nm)
    l_tm.append(tm)
    l_opp.append(opp)
    l_pos.append(pos)
    l_sal.append(sal)
    l_mins.append(mins)
    l_pts.append(pts)

#build dataframe from lists
pd_data = pd.DataFrame(
    {'name': l_names,
     'team': l_tm,
     'pos': l_pos,
     'opp': l_opp,
     'sal': l_sal,
     'mins': l_mins,
     'pts': l_pts,
     'date' : date
    })

print(pd_data)
#old system to CSV
pd_data.to_csv(date + '_fd_lineup.csv')

#iterate through dataframe to insert new records to lineup_fd table
for index, row in pd_data.iterrows():
    insert_query = '''insert into LINEUP_FD (NAME, GDATE,RW_MIN, RW_PTS, SAL, OPP, POS, TM) 
               values (lower(:1),TO_DATE(:2,'mm_dd_yyyy'),:3,:4,:5,:6,:7,:8)'''

    val1 =str(pd_data.iloc[index]['name'])
    val2 =str(pd_data.iloc[index]['date'])
    val3 = str( pd_data.iloc[index]['mins'])
    val4 =str(pd_data.iloc[index]['pts'])
    val5 = str( pd_data.iloc[index]['sal'])
    val6 =str(pd_data.iloc[index]['opp'])
    val7 =str(pd_data.iloc[index]['pos'])
    val8 = str( pd_data.iloc[index]['team'])

    cur.execute(insert_query,
    (val1,val2,val3,val4,val5,val6,val7,val8))
    conn.commit()
        
#close database connection        
cur.close()
conn.close() 
print("done")