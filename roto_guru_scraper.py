# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:03:19 2016

@author: tpauley
"""

import requests
import bs4
import pandas as pd
import datetime
import cx_Oracle
#import cx_Oracle as oracle

 #import cx_Oracle as oracle
ip = 'localhost'
port = 1522
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)
oracle_con = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
oracle_cur = oracle_con.cursor()   

oracle_query = "select GURU_ID, REPLACE(GURU_URL,'playrh','playrh16') as GURU_URL from SCRAPING_ROTO_GURU_BASE"

url_df = pd.read_sql_query(oracle_query,oracle_con)
rg_list = url_df['GURU_URL'][:5].tolist()


def rg_url_scraper(urls):
    ret_df = pd.DataFrame()
    for url in urls:
        if url[29:39] == 'playrh.cgi':
            season = '2016'
        if url[29:39] == 'playrh16.c':
            season = '2015'
        if url[29:39] == 'playrh15.c':
            season = '2014'
        
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
        
        ret_df = pd.concat([ret_df,pd_data])
    return ret_df


new_df = rg_url_scraper(rg_list)
print(new_df[['name','season','gdate']])
oracle_cur.close()
oracle_con.close()