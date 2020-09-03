# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 15:05:50 2020

@author: 33849
"""
# Ch 4 in P4e - loops
TARGET = 100000
INTERESTRATE = 0.02
year = 0
balance = 5000
while balance < TARGET:
    year = year + 1
    interest = INTERESTRATE * balance
    balance = balance + interest
    print(balance,year)
    
count = 0
while count < 10:
    count += 1
    print(count)
    

