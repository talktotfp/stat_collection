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

 #import cx_Oracle as oracle
ip = 'localhost'
port = 1522
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)



oracle_con = cx_Oracle.connect('nba', 'rp4490', dsn_tns)
oracle_cur = oracle_con.cursor()   



url_list = []
for c in ascii_lowercase:
    try:
        crawler = requests.get('http://www.basketball-reference.com/players/'+str(c)+'/')
        crawl_soup = bs4.BeautifulSoup(crawler.text,"lxml")

        crawl_table = crawl_soup.find('table')

        for row in crawl_table.find_all('tr')[0:]:
            for row in row.find_all('strong')[0:]:
                crawler_name = row.find('a', href=True)
                crawler_url = 'http://www.basketball-reference.com/'+crawler_name['href'].replace('.html','')+'/gamelog/2017'
                url_list.append(crawler_url)
    except Exception as e:
        pass

#get text from HTML document as response
pd_url_list = pd.DataFrame({'href' : url_list})

#for index, row in pd_url_list.iterrows():
for index, row in pd_url_list.iterrows():
    try:
            
        response = requests.get(str(pd_url_list.iloc[index]['href']))
        
        #setup BeaufifulSoup 
        soup = bs4.BeautifulSoup(response.text,"lxml")
        
        
        # Create an object of the first object that is class=dataframe
        table = soup.find('tbody')
        
        name = soup.find("h1", {"itemprop":"name"}).string.replace("2016-17 Game Log","").strip()
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
        
        
        
        # Find all the <tr> tag pairs, skip the first one, then for each.
        for row in table.find_all('tr')[len(row)-1:]:
            try:
                # Create a variable of all the <td> tag pairs in each <tr> tag pair,
                col = row.find_all('td')
        
                # Create a variable of the string inside 1st <td> tag pair,
                c_g = col[0].string.strip()
                c_name = col[1].string.strip()
                c_gdate = col[1].string.strip()
                c_age = col[2].string.strip()
                c_team = col[3].string.strip()
                c_opp = col[5].string.strip()
                if col[4].text == '':
                    c_home = '0'
                else:
                    c_home = '1'
                #c_home = col[4].text
                c_gs = col[7].string.strip()
                c_mp = col[8].string.strip()
                c_fgm = col[9].string.strip()
                c_fga = col[10].string.strip()
                
                c_tpm = col[12].string.strip()
                c_tpa = col[13].string.strip()
                
                c_ftm = col[15].string.strip()
                c_fta = col[16].string.strip()
                
                c_orb = col[18].string.strip()
                c_drb = col[19].string.strip()
                c_trb = col[20].string.strip()
                c_ast = col[21].string.strip()
                c_stl = col[22].string.strip()
                c_blk = col[23].string.strip()
                c_tov = col[24].string.strip()
                c_pf = col[25].string.strip()
                c_pts = col[26].string.strip()
                c_gmsc = col[27].string.strip()
                # and append it to first_name variable
                l_g.append(c_g)
                l_name.append(name)
                l_gdate.append(c_gdate)
                l_age.append(c_age)
                l_team.append(c_team)
                l_opp.append(c_opp)
                l_home.append(c_home)
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
                l_gmsc.append(c_gmsc)
                
            except Exception as e:
                pass
            
        #build dataframe from lists
        pd_data = pd.DataFrame(
            {'a1_l_name' : l_name,
            'a1_l_g' : l_g,
            'l_gdate' : l_gdate,
            'l_age' : l_age,
            'l_team' : l_team,
            'l_opp' : l_opp,
            'l_home' : l_home,
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
            'l_gmsc' : l_gmsc
            })
        print(name + ' Done')
        print(pd_data)
        for index, row in pd_data.iterrows():
            try:
                    
                insert_query = '''insert into PGAME_BUFFER (NAME, GDATE,G, AGE, TM, OPP, GS, 
                MP, FGM, FGA,  TPM, 
                TPA,  FTM, FTA, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, GMSC, HOME)
                   values (lower(:1),TO_DATE(:2,'yyyy-mm-dd'),:3,
                :4,
                :5,
                :6,
                :7,
                :8,
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
                :26,
                :27,
                :28
                )'''
                
                val1 =str(pd_data.iloc[index]['a1_l_name'])
                val2 =str(pd_data.iloc[index]['l_gdate'])
                val3 = str( pd_data.iloc[index]['a1_l_g'])
                val4 =str(pd_data.iloc[index]['l_age'])
                val5 = str( pd_data.iloc[index]['l_team'])
                val6 =str(pd_data.iloc[index]['l_opp'])
                val7 =str(pd_data.iloc[index]['l_gs'])
                val8 = str( pd_data.iloc[index]['l_mp'])
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
                val27 =str(pd_data.iloc[index]['l_gmsc'])
                val28 =str(pd_data.iloc[index]['l_home'])
                oracle_cur.execute(insert_query,
                             (val1,val2,val3,val4,val5,val6,val7,val8,val9,
                              val10,val12,val13,val15,val16,val18,
                              val19,val20,val21,val22,val23,val24,val25,val26,val27, val28))
                oracle_con.commit()
            except Exception as e:
                logging.exception("message")
    except Exception as e:
        pass
oracle_cur.close()
oracle_con.close()




