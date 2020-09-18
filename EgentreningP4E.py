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

#Trix oppgaver UiO - funksjoner
#Noen telle-funksjoner
#a
def antallsifre(tall):
    sifre = len(str(tall))
    return sifre

test1 = antallsifre(input("Oppgi et vilkårlig stort heltall: "))
test2 = antallsifre(input("Oppgi enda et vilkårlig stort heltall: "))

print("Antallet sifre i første tall er",test1)
print("Antallet sifre i andre tall er",test2)

#b
def antallGittBokstav(ord,bokstav):
    teller = 0
    for tegn in ord:
        if tegn == bokstav:
            teller += 1
    return teller

test3 = antallGittBokstav("sommerferie","e")
test4 = antallGittBokstav("sommerferie","a")

def strengLengreEnnTall(streng,tall):
    if len(streng) > tall:
        return True
    else: 
        return False

test5 = strengLengreEnnTall("to",4)
test6 = strengLengreEnnTall("sommerferie",2)
print(test5)
print(test6)

#Enkle prosedyrer og funksjoner
#a
def velkommen(bruker):
    print("Hei, "+bruker+"!")
    
brukernavn = input("Oppgi ditt brukernavn: ")
velkommen(brukernavn)

#Alternativt:
def hallo(x):
    print("Hei, "+x+"!")
    return x

navn = input("Oppgi ditt navn: ")
hallo(navn)
#Lærdom: Kun nødvendig å etablere en sammenheng mellom formalargument og videre prosessering i funksjonskroppen
#Kan senere kalle funksjonene med en hvilken som helst tekststring, så vil denne stringen prosesseres på samme måte
#som formalargumentet "x" i funksjonsdefinisjonen. 

navn1 = hallo(input("Oppgi ditt navn: "))
#OBS: Resultatet av funksjonskallet over er et "NoneType object". Dette fordi "funksjonen" hallo egentlig ikke er en 
#funksjon, men kun en prosedyre. hallo() er ikke definert med en returverdi, og derfor gir funksjonskallet den spesielle
#verdien None i retur. Kan ikke brukes til noe.

def strenginator(streng1,streng2):
    return streng1+streng2

konkatenert = strenginator("hipp","hurra")
print(konkatenert)

#Fibonacci-sekvens
def finnAlleFibTall(oppTil):
    
#Ch. 9 - Classes and objects
#Trening etter Corey Schafer, Youtube

class Employee:

    def __init__(self, first_name, last_name, birthday, location):
        """Initializing each employee with the basic information of first name,
        last name, date of birth and location"""
        
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday #yyyymmdd
        self.location = location
        self.email = first_name + "." + last_name + "@kystverket.no"
        self.full_name = first_name + " " + last_name
        
    def 
       
        
emp1 = Employee("Magnus", "Skeie", 19890522, "Arendal")

print(emp1.first_name)
print(emp1.email)
print(emp1.full_name)



class Student:
    """Register students with names, birthday, university and department, to be able to generate their student email
    adress"""
    
    def __init__(self, first_name, middle_name, last_name, birthday, university, department):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.birthday = birthday #yyyymmdd
        self.university = university
        self.department = department
    

    def uni_abbreviation(self):
        if self.university == "Universitetet i Oslo":
            self.uni_abbreviation = "UiO"
            return self.uni_abbreviation
        elif self.university == "Universitetet i Tromsø":
            self.uni_abbreviation = "UiT"
            return self.uni_abbreviation
        elif self.university == "Universitetet i Bergen":
            self.uni_abbreviation = "UiB"
            return self.uni_abbreviation
        elif self.university == "Universitetet i Agder":
            self.uni_abbreviation = "UiA"
            return self.uni_abbreviation
    
    def dept_abbreviation(self):
        if self.department == "Samfunnsvitenskapelig fakultet":
            self.dept_abbreviation = "SV"
            return self.dept_abbreviation
        elif self.department == "Humanistisk fakultet":
            self.dept_abbreviation = "HF"
            return self.dept_abbreviation
        elif self.department == "Matematisk naturvitenskapelig fakultet":
            self.dept_abbreviation = "MN"
            return self.dept_abbreviation
        elif self.department == "Utdanningsvitenskapelig fakultet":
            self.dept_abbreviation = "UV"
            return self.dept_abbreviation
    
    def uni_email(self):
        if self.middle_name == "-":
            self.uni_email = self.first_name.lower() + "." + self.last_name.lower() + "@student." + self.dept_abbreviation.lower() + "." + self.uni_abbreviation.lower() + ".no"
            return self.uni_email 
        elif self.middle_name != "-":
            self.uni_email = self.first_name.lower() + "." + self.middle_name.lower() + "." + self.last_name.lower() + "@student." + self.dept_abbreviation.lower() + "." + self.uni_abbreviation.lower() + ".no"
            return self.uni_email 
   
student_1 = Student('Magnus', 'Aagaard', 'Skeie', 19890522, 'Universitetet i Oslo', 'Samfunnsvitenskapelig fakultet')
student_2 = Student('Student2fname', '-', 'Student2lname', 19890517, 'Universitetet i Bergen', 'Humanistisk fakultet')
student_3 = Student('Student3fname', '-', 'Student3lname', 19890401, 'Universitetet i Tromsø', 'Matematisk naturvitenskapelig fakultet')
student_4 = Student('Student4fname', '-', 'Student4lname', 19890101, 'Universitetet i Agder', 'Utdanningsvitenskapelig fakultet')

print(student_1.uni_abbreviation())
print(student_1.dept_abbreviation())
print(student_2.uni_abbreviation())
print(student_2.dept_abbreviation())
print(student_3.uni_abbreviation())
print(student_3.dept_abbreviation())
print(student_4.uni_abbreviation())
print(student_4.dept_abbreviation())
print(student_3.birthday)
print(student_4.first_name)
print(student_4.middle_name)

student_1.uni_email = Student.uni_email(student_1)
student_2.uni_email = Student.uni_email(student_2)
student_3.uni_email = Student.uni_email(student_3)
student_4.uni_email = Student.uni_email(student_4)

print(student_1.uni_email)
print(student_2.uni_email)
print(student_3.uni_email)
print(student_4.uni_email)    
        
student_5 = Student('Student5fname', '-', 'Student5lname', 20000101, 'Universitetet i Agder', 'Utdanningsvitenskapelig fakultet')
print(student_5.first_name)
print(student_5.middle_name)
print(student_5.last_name) 
print(student_5.birthday) 
print(student_5.university) 
print(student_5.department)






























    













































        