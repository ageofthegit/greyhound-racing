# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 09:10:54 2022

@author: karan
"""

import yaml


with open('C:\\Users\\karan\\Documents\\Code\\racing\\config.yml', 'r') as file:
    config = yaml.safe_load(file)

print(config)

