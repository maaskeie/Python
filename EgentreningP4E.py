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
    
#Comparing adjacent values
value = 0.0
inputStr = input("Enter an integer value: ")
while inputStr != "" :
    previous = value
    value = float(inputStr) 
    if value == previous :
        print("Duplicate input")
    inputStr = input("Enter an integer value: ")
    
#For loops
for i in range(1,10,2) :
    print(i)

for number in range(10) :
    print(number)
    
count = 0
for i in range(1,1000000,2) :
    count += 1
print("Det er",count,"oddetall i sekvensen.")

#Printing a table

#Initialize maximum values for the max ranges (determining no. of rows and columns)
NMAX = 4
XMAX = 10

#Print tabel header
print()
for n in range(1, NMAX + 1) :
    print("%10d" % n, end="")
    
print()
for n in range(1, NMAX + 1) :
    print("%10s" % "x", end="")

print("\n", "      ", "-" * 33)

#Print table body
for x in range(1, XMAX + 1):
    for n in range(1, NMAX + 1):
        print("%10.0f" % x ** n, end="" )
    print()

#Printing some patterns

for i in range(5):
    for j in range(4):
        print("*", end="")
    print()
    
for i in range(10):
    for j in range(50):
        if i % 2 == 1: 
            if j % 2 == 1:
                print("*", end="")
            else:
                print("-", end="")
        else:
            if j % 2 == 0:
                print("*", end="")
            else:
                print("-", end="")
    print()
    
#Evaluating strings
#Finding matches    

string = input("Oppgi en rekke med bokstaver og/eller tall: ")
found = False
position = 0
while not found and position < len(string):
    if string[position].isdigit():
        found = True
    else:
        position +=1
if found:
    print("The first digit of the string is in position",position)
else:
    print("The string does not contain a character")

#Functions (ch. 5)
def summation(a,b,c):
    sum = a + b + c
    return sum
    print(sum)
summation(3,4,5)

def cubeVolume(sideLength):
    if sideLength > 0 :
        volume = sideLength ** 3
    else:
        volume = 0
    return volume

sideLength1 = int(input("Oppgi en lengde i cm: "))
sideLength2 = int(input("Oppgi en ny lengde i cm: "))
sideLength3 = int(input("Oppgi enda en ny lengde i cm: "))

result1 = cubeVolume(sideLength1)
result2 = cubeVolume(sideLength2)
result3 = cubeVolume(sideLength3)

print()
print("The volume of a cube with side length",sideLength1,"is",result1,"cm3")
print("The volume of a cube with side length",sideLength2,"is",result2,"cm3")
print("The volume of a cube with side length",sideLength3,"is",result3,"cm3")

#Function that takes two integer values from user as a low and high boundry
def readIntBetween(low, high):
    value = int(input("Enter a value between " + str(low) + " and " + str(high) + " : "))
    while value < low or value > high :
        print("Error: Invalid entry")
        value = int(input("Enter a value between " + str(low) + " and " + str(high) + " : "))
    return value

readIntBetween(5,10)

#Example from textbook
def main():
    print("Please enter a time: hours, then minutes. ")
    hours = readIntBetween(0,23)
    minutes = readIntBetween(0,59)
    print("You entered"" %d hours and %d minutes." % (hours,minutes))
def readIntBetween(low,high):
    value = int(input("Enter a value between " + str(low) + " and " + str(high) + " : "))
    while value < low or value > high :
        print("Error: Invalid entry")
        value = int(input("Enter a value between " + str(low) + " and " + str(high) + " : "))
    return value

main()







        