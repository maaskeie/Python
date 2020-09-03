# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 14:35:23 2020

@author: 33849
"""

#Egen triksing med nested branches
# Program som tar inn sivilstatus og inntektsnivå, og skriver ut skatten du må betale

x = (0,100000,200000,300000,500000)
y = [0,50000,100000,150000,250000]
sivilstatus = input("Er du gift? (ja/nei): ")
inntekt = int(input("Oppgi din årsinntekt (til nærmeste 100.000): "))
if sivilstatus in ["ja","Ja"]:
    print('ja')
    if inntekt < 100000 :
        print("Du skal betale",x[0],"kroner i skatt")
    elif inntekt >= 100000 and inntekt < 300000 :
        print("Du skal betale",x[1],"kroner i skatt")
    elif inntekt >=300000 and inntekt < 700000 :
        print("Du skal betale",x[2],"kroner i skatt")
    elif inntekt >= 700000 and inntekt < 1000000 :
        print("Du skal betale",x[3],"kroner i skatt")
    elif inntekt >= 1000000 :
        print("Du skal betale",x[4],"kroner i skatt")
else : 
    print('nei')
    if inntekt < 100000 :
        print("Du skal betale",y[0],"kroner i skatt")
    elif inntekt >= 100000 and inntekt < 300000 :
        print("Du skal betale",y[1],"kroner i skatt")
    elif inntekt >=300000 and inntekt < 700000 :
        print("Du skal betale",y[2],"kroner i skatt")
    elif inntekt >= 700000 and inntekt < 1000000 :
        print("Du skal betale",y[3],"kroner i skatt")
    elif inntekt >= 1000000 :
        print("Du skal betale",y[4],"kroner i skatt")

# Grafiske fremstillinger
from matplotlib import pyplot
pyplot.bar([1,2,3,4,5,6,7,8,9,10], [1,3,5,9,10,16,19,25,39,72])
pyplot.xlabel("År")
pyplot.ylabel("Verdier")

x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
y = [2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40]
pyplot.plot(x,y,"r-.*")
pyplot.title("f(x) = 2x")
pyplot.xlabel("x-verdier")
pyplot.ylabel("y-verdier")
pyplot.grid("on")
pyplot.xlim(0,30)
pyplot.ylim(0,50)















