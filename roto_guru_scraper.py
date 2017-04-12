# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:03:19 2016

"""

import requests
import bs4
import numpy as np
import pandas as pd
import datetime
import pymysql
import cx_Oracle


#ip = 'localhost'
#port = 1522
#SID = 'xe'
#dsn_tns = cx_Oracle.makedsn(ip, port, SID)
#
#
##connect to MySQL database
#conn = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
##create connection cursor
#cur = conn.cursor()

#http://rotoguru1.com/cgi-bin/playrh16.cgi?4374x
#get text from HTML document as response
urls = ['http://rotoguru1.com/cgi-bin/playrh.cgi?4374x','http://rotoguru1.com/cgi-bin/playrh.cgi?3768x']

for url in urls:
    if url[29:39] == 'playrh.cgi':
        season = '2016-2017'
    if url[29:39] == 'playrh16.c':
        season = '2015-2016'
    if url[29:39] == 'playrh15.c':
        season = '2014-2015'
    
    response = requests.get(url)
    
    #setup BeaufifulSoup 
    soup = bs4.BeautifulSoup(response.text,"lxml")
    
    
    #find table in HTML by looking for 'tr' table row objects
    table_body = soup.find_all('table')
    rows = table_body[5].find_all('tr')
    
    
    #build blank lists to be filled in
    l_gdate = []
    l_opp = []
    l_mins = []
    l_fdp = []
    l_fds = []
    l_ddp = []
    l_dds = []
    l_dkp = []
    l_dks = []
    l_yhp = []
    l_yhs = []
    
    date = datetime.datetime.today().strftime("%m_%d_%Y")
    
    #loop through all rows in HTML (table_body find all 'td')
    for rows in rows[10:]:
        
        col = rows.find_all('td')
        if len(col) < 11:
            break
        
        gdate = col[0].text.strip()
        opp = col[1].text.strip()
        mins = col[2].text.strip()
        fdp = col[3].text.strip()
        fds = col[4].text.strip()
        ddp = col[5].text.strip()
        dds = col[6].text.strip()
        dkp = col[7].text.strip()
        dks = col[8].text.strip()
        yhp = col[9].text.strip()
        yhs = col[10].text.strip()
        l_gdate.append(gdate)
        l_opp.append(opp)
        l_mins.append(mins)
        l_fdp.append(fdp)
        l_fds.append(fds)
        l_ddp.append(fdp)
        l_dds.append(fds)
        l_dkp.append(fdp)
        l_dks.append(fds)
        l_yhp.append(fdp)
        l_yhs.append(fds)
    
    
    pos_html = soup.find_all('font')
    
    
    b_html = soup.find_all('b')
    name = b_html[1].text.replace('\n','')
    team = b_html[2].text.replace('\n','')
    fd_pos = b_html[3].text
    dd_pos = b_html[4].text
    dk_pos = b_html[5].text
    yh_pos = b_html[6].text
    
    a_html = soup.find_all('a')
    espn_link = a_html[1]['href']
    nba_link = a_html[2]['href']
    rotowire_link = a_html[3]['href']
    rotoworld_link = a_html[4]['href']
    #team = a_html[2].text.replace('\n','')
    #fd_pos = a_html[3].text
    #dd_pos = a_html[4].text
    #dk_pos = a_html[5].text
    #yh_pos = a_html[6].text
    #   
        
    #build dataframe from lists
    pd_data = pd.DataFrame(
        {'name': name,
         'gdate': l_gdate,
         'opp': l_opp,
         'mins': l_mins,
         'fdp': l_fdp,
         'fds': l_fds,
         'ddp': l_ddp,
         'dds': l_dds,
         'dkp': l_dkp,
         'dks': l_dks,
         'yhp': l_yhp,
         'yhs': l_yhs,
         'season': season,
         'team': team,
         'fd_pos': fd_pos,
         'dd_pos': dd_pos,
         'dk_pos': dk_pos,
         'yh_pos': yh_pos,
         'espn_link': espn_link,
         'nba_link': nba_link,
         'rotowire_link': rotowire_link,
         'rotoworld_link': rotoworld_link
        })
    
    print(pd_data[['gdate','name','dkp','dks']])
    
    
    #iterate through dataframe to insert new records to lineup_fd table
    #for index, row in pd_data.iterrows():
    #    insert_query = '''insert into LINEUP_FD (NAME, GDATE,RW_MIN, RW_PTS, SAL, OPP, POS, TM) 
    #               values (lower(:1),TO_DATE(:2,'mm_dd_yyyy'),:3,:4,:5,:6,:7,:8)'''
    #
    #    val1 =str(pd_data.iloc[index]['name'])
    #    val2 =str(pd_data.iloc[index]['date'])
    #    val3 = str( pd_data.iloc[index]['mins'])
    #    val4 =str(pd_data.iloc[index]['pts'])
    #    val5 = str( pd_data.iloc[index]['sal'])
    #    val6 =str(pd_data.iloc[index]['opp'])
    #    val7 =str(pd_data.iloc[index]['pos'])
    #    val8 = str( pd_data.iloc[index]['team'])
    #
    #    cur.execute(insert_query,
    #    (val1,val2,val3,val4,val5,val6,val7,val8))
    #    conn.commit()
    #        
    ##close database connection        
    #cur.close()
    #conn.close() 
    #print("done")
