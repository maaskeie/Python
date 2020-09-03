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
    
#Common loop algorithms
# Calculating total and average
total = 0.0
inputStr = input("Oppgi et beløp med 1 desimal :")
while inputStr != "" :
    value = float(inputStr)
    total = total + value
    inputStr = input("Oppgi et beløp med 1 desimal :")
print("Summen er",total)
    

total = 0.0
count = 0
inputStr =input("Oppgi et beløp med 1 desimal (bruk punktum som skilletegn) :")
while inputStr != "" :
    value = float(inputStr)
    total = total + value
    count += 1
    inputStr = input("Oppgi et beløp med 1 desimal (bruk punktum som skilletegn) :")
if count != 0 :
    average = total / count
    print("Gjennomsnittet er",average)
else :
    average = 0.0
    print("Ingen tall er oppgitt. Gjennomsnittet er",average)
    
    