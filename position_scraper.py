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

    



#oracle_con = cx_Oracle.connect('tylerp/tp323ean@ukudbsh1/ukm25d')
#oracle_cur = oracle_con.cursor()

url_list = []
for c in ascii_lowercase:
    try:
        crawler = requests.get('http://www.basketball-reference.com/players/'+str(c)+'/')
        crawl_soup = bs4.BeautifulSoup(crawler.text,"lxml")

        crawl_table = crawl_soup.find('table')

        for row in crawl_table.find_all('tr')[0:]:
            for row in row.find_all('strong')[0:]:
                crawler_name = row.find('a', href=True)
                crawler_url = 'http://www.basketball-reference.com/'+crawler_name['href'].replace('.html','')+'/gamelog/2016'
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
        for row in soup.find_all('p')[0:]:
            print(row.string)

        print(name)
        

    except Exception as e:
        pass
#oracle_cur.close()
#oracle_con.close()




