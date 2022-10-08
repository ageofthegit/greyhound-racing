# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------- DETAILS

"""
OUTLINES
    

NEXT STEPS    


"""

#----------------------------------------------------------------------------- LIBRARIES

import pandas as pd, numpy as np, calendar
import helpdesk as hd
import datetime

# Import libraries
from datetime import datetime
from datetime import timedelta
from dateutil import tz

import math

import numpy as np
import pandas as pd

from scipy.stats import zscore
from sklearn.linear_model import LogisticRegression

import betfairlightweight
from betfairlightweight import filters

import sys, os


# Import the necessary libraries to webscrape the publications
import requests, urllib
from bs4 import BeautifulSoup as soup

#----------------------------------------------------------------------------- VARIABLES

#--------------------------------------- User Defined

# Adding the racing folder to the PATH variable 
sys.path.append('C:\\Users\\karan\\Documents\\Code\\racing')
print(sys.path)

class Data(object):
    pass

DEBUG = True

df = Data()
summ = Data()

#--------------------------------------- Retrieve Sensitive Variables

BETFAIR_USERNAME = os.environ.get('BETFAIR_USERNAME')
BETFAIR_PASSWORD = os.environ.get('BETFAIR_PASSWORD')
BETFAIR_APP_KEY = os.environ.get('BETFAIR_APP_KEY')



#--------------------------------------- Websites

# First define the url of interest
url = "https://promo.betfair.com/betfairsp/prices"
base = "https://promo.betfair.com"



#------------------------------------------------------------------------------ MAIN CODE


#--------------------------------------- Tutorial for Beautiful Soup

# Once you have set the url, we can now use the requests library to get the content of the url's html page.

print(url)
html_page = requests.get(url).content

# Now we have the html page we are going to use Beautiful Soup to put the information into a more readable format and then print it below. We call this a soup page.
soup_page = soup(html_page, "html")
print(soup_page)



# First, notice that each <> that starts with "a" always contains text while <>'s not containing "a" look more like commands telling the html page where a button, or other design element should be. Let's use this to do our first filter.
#soup_page.findAll("a")

# Save the filtered information as an instance
#links = soup_page.findAll("a",{"class": "views-list-image"})
links = soup_page.findAll("a")

print(links)



# Now that we have the links we can pull out the link to each of the pages where you can download the reports of interest
# print sample, element #0
print(links[0].attrs["href"])



# A short loop to save the weblinks to each of the publications
pub_links = []
for link in links:
    pub_links.append(base + link.attrs["href"])

# Print sample of pub_links
print(pub_links[0])


# Last part of the pub_links
print(pub_links[0].split('/')[-1])


# Find the total number of files available for download
print(len(pub_links))
# 50221



# 12 records per day, 
## select the 8th day from the past to the 10th day from the past

date_of_first = pd.to_datetime('2022-01-01', format = '%Y-%m-%d').date()
date_of_last = pd.to_datetime('2022-09-30', format = '%Y-%m-%d').date()

print( (date_of_last - date_of_first).days)

run_loop_for = (date_of_last - date_of_first).days

#for i in range(12*7 , 12*run_loop_for):
for i in range(12*run_loop_for , 12*run_loop_for + 12*10 ):
    
    file_url = pub_links[i]
    #print(file_url)
    
    #if ('greyhound' in file_url) & ('win' in file_url) :
    if ('greyhound' in file_url) & ('place' in file_url) :
        #print(file_url)
        file_name = file_url.split('/')[-1]
        location_on_pc = 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Place\\' + file_name

        #print(location_on_pc)
        print(file_name)        
        urllib.request.urlretrieve(file_url,location_on_pc)
        
    if ('greyhound' in file_url) & ('win' in file_url) :
        #print(file_url)
        file_name = file_url.split('/')[-1]
        location_on_pc = 'D:\\GDrive\\Analyticsflex\\Racing\\Data_dwbfprices\\Win\\' + file_name

        #print(location_on_pc)
        print(file_name)        
        urllib.request.urlretrieve(file_url,location_on_pc)













