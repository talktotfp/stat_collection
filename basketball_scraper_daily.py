# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 15:10:20 2016

@author: tpauley
"""

import requests
import bs4
import pandas as pd
import logging
from string import ascii_lowercase
import cx_Oracle
#import cx_Oracle as oracle
ip = 'localhost'
port = 1522
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)



oracle_con = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
oracle_cur = oracle_con.cursor()
l_g = []
l_name = []
l_gdate = []
l_age = []
l_team = []
l_opp = []
l_home = []
l_gs = []
l_mp = []
l_fgm = []
l_fga = []
l_fgp = []
l_tpm = []
l_tpa = []
l_tpp = []
l_ftm = []
l_fta = []
l_ftp = []
l_orb = []
l_drb = []
l_trb = []
l_ast = []
l_stl = []
l_blk = []
l_tov = []
l_pf = []
l_pts = []
l_gmsc = []


#get text from HTML document as response

response = requests.get('http://www.basketball-reference.com/friv/last_n_days.cgi?n=1')

#setup BeaufifulSoup 
soup = bs4.BeautifulSoup(response.text,"lxml")


# Create an object of the first object that is class=dataframe
table = soup.find_all('tr')
for row in table:
    col = row.find_all('td')
    if (len(col) == 24) :
      
        c_name = col[0].string.strip()
        c_gs = col[3].string.strip()
        c_team = col[1].string.strip()
        c_mp = col[4].string.strip()
        c_fgm = col[5].string.strip()
        c_fga = col[6].string.strip() 
        c_tpm = col[8].string.strip()
        c_tpa = col[9].string.strip()        
        c_ftm = col[11].string.strip()
        c_fta = col[12].string.strip()       
        c_orb = col[14].string.strip()
        c_drb = col[15].string.strip()
        c_trb = col[16].string.strip()
        c_ast = col[17].string.strip()
        c_stl = col[18].string.strip()
        c_blk = col[19].string.strip()
        c_tov = col[20].string.strip()
        c_pf = col[21].string.strip()
        c_pts = col[22].string.strip()

        l_name.append(c_name)
        l_team.append(c_team)
        l_gs.append(c_gs)
        l_mp.append(c_mp)
        l_fgm.append(c_fgm)
        l_fga.append(c_fga)        
        l_tpm.append(c_tpm)
        l_tpa.append(c_tpa)        
        l_ftm.append(c_ftm)
        l_fta.append(c_fta)        
        l_orb.append(c_orb)
        l_drb.append(c_drb)
        l_trb.append(c_trb)
        l_ast.append(c_ast)
        l_stl.append(c_stl)
        l_blk.append(c_blk)
        l_tov.append(c_tov)
        l_pf.append(c_pf)
        l_pts.append(c_pts)


        
        
        
        # Find all the <tr> tag pairs, skip the first one, then for each.
#for row in table[2].find_all('tr')[:]:
#  #print(row)
##    # Create a variable of all the <td> tag pairs in each <tr> tag pair,
#    col = row.find_all('td')
#    print(col[1])
##    # Create a variable of the string inside 1st <td> tag pair,
##
#    
#build dataframe from lists
pd_data = pd.DataFrame(
    {'a1_l_name' : l_name,
    'l_team' : l_team,
    'l_gs' : l_gs,
    'l_mp' : l_mp,
    'l_fgm' : l_fgm,
    'l_fga' : l_fga,  
    'l_tpm' : l_tpm,
    'l_tpa' : l_tpa,  
    'l_ftm' : l_ftm,
    'l_fta' : l_fta,    
    'l_orb' : l_orb,
    'l_drb' : l_drb,
    'l_trb' : l_trb,
    'l_ast' : l_ast,
    'l_stl' : l_stl,
    'l_blk' : l_blk,
    'l_tov' : l_tov,
    'l_pf' : l_pf,
    'l_pts' : l_pts,
    })
##        
for index, row in pd_data.iterrows():

    insert_query = '''insert into PGAME_BUFFER (NAME, GDATE,  TM,  GS, 
    MP, FGM, FGA,  TPM, 
    TPA,  FTM, FTA, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS)
       values (lower(:1),(TRUNC(SYSDATE)-1),   
    :5,   
    :7,
    :8||':00',
    :9,
    :10,  
    :12,
    :13, 
    :15,
    :16,   
    :18,
    :19,
    :20,
    :21,
    :22,
    :23,
    :24,
    :25,
    :26
    )'''
##    
    val1 =str(pd_data.iloc[index]['a1_l_name'])

    val5 = str( pd_data.iloc[index]['l_team'])

    val7 =str(pd_data.iloc[index]['l_gs'])
    val8 =str( pd_data.iloc[index]['l_mp'])
    val9 =str(pd_data.iloc[index]['l_fgm'])
    val10 =str(pd_data.iloc[index]['l_fga'])
    
    val12 =str(pd_data.iloc[index]['l_tpm'])
    val13 =str(pd_data.iloc[index]['l_tpa'])
    
    val15 =str(pd_data.iloc[index]['l_ftm'])
    val16 =str(pd_data.iloc[index]['l_fta'])
    
    val18 =str(pd_data.iloc[index]['l_orb'])
    val19 =str(pd_data.iloc[index]['l_drb'])
    val20 = str( pd_data.iloc[index]['l_trb'])
    val21 =str(pd_data.iloc[index]['l_ast'])
    val22 =str(pd_data.iloc[index]['l_stl'])
    val23 = str( pd_data.iloc[index]['l_blk'])
    val24 =str(pd_data.iloc[index]['l_tov'])
    val25 =str(pd_data.iloc[index]['l_pf'])
    val26 = str( pd_data.iloc[index]['l_pts'])

    try:
        oracle_cur.execute(insert_query,
                     (val1,val5,val7,val8,val9,
                      val10,val12,val13,val15,val16,val18,
                      val19,val20,val21,val22,val23,val24,val25,val26 ))
        oracle_con.commit()
        print(val1, ' Done')
    except Exception as e:
        print(val1,'  ERROR --------------')
        logging.exception("message")
        
oracle_cur.execute('insert into DAILY_TRIGGERS (TRIGGER_ID, GDATE) (select S_TRIG.NEXTVAL, trunc(sysdate) from dual)')
oracle_con.commit()            
oracle_cur.close()
oracle_con.close()



