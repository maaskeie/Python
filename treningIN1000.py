HoydeAar=[50,76,87,95]
sum = HoydeAar[0] + HoydeAar[3]
print(sum, "cm")

print("Hvilken alder vil du vite høyden for?")
svar=int(input("0, 1, 2 eller 3 år? "))
print(HoydeAar[svar], "cm")

liste1=[]
liste1.append(50)
liste1.append(100)

print([50,100] + [150,200])
HoydeAar = HoydeAar + [150,200]

len(HoydeAar)

50 in HoydeAar

HoydeAar.append(150)

HoydeAar.count(150)
HoydeAar.sort()

min_liste1=[0,2,5,3,6,7,8,9,3,5,6,4,3,2,4,5,6,7,87,6,5,5,6,7,7,8,854,3335,543,677,876,554,443,3335,6667,78,9]

min_liste2=[]

min_liste2.append(3)

min_liste1.sort()

list(min_liste1)

len(min_liste1)

min_liste1[36]=2

min_liste2.append(4)
min_liste2 = min_liste2 + [5,6,7,8,9,10,11,12,13,14,15,16]

min_liste1.append(min_liste2)
list(min_liste1)
len(min_liste1)

min_liste1.remove(0)
list(min_liste1)
print(min_liste1[36])

min_liste1.remove(36)

min_liste1.count(2)

min_liste3=[]

min_liste4=[1,2,3,4]

min_liste3.append(2)
min_liste3.append(3)

min_liste3.append(min_liste4)

print(min_liste3[2][1])

tysk_ordbok1={"God dag":"Guten Tag","Hvordan går det?":"Wie geht's?","Hvor gammel er du?":"Wo alt bist du?","Hvor kommer du fra?":"Wo kommen Sie aus?"}

tysk_ordbok1["Hva heter du?"]= "Wie heisst du?"

list(tysk_ordbok1)

tysk_ordbok1["Hva heter du?"]

######################################
#TRIX MENGDETRENINGSOPPGAVER 10.08.20
######################################

#1
hello = "Hello"
world = "World"
print(hello,world)

print(hello+"?",world+"?")

#2
heltall1 = int(input("Oppgi et heltall: "))
heltall2 = int(input("Oppgi et annet heltall: "))
diff = abs(heltall1 - heltall2)
print("Differansen mellom tallene er ", diff, sep="")

#3
heltall1 = int(input("Oppgi et heltall: "))
heltall2 = int(input("Oppgi et annet heltall: "))
produkt = heltall1 * heltall2
print("Produktet av",heltall1,"og",heltall2,"er",produkt)

#4
first = int(input("Oppgi et vilkårlig tall: "))
if first < 10:
    print("Tallet er mindre enn 10.")
elif first > 10 and first < 20:
    print("Tallet er mellom 10 og 20.")
else: print("Tallet er større enn 20.") 

#5
temp = float(input("Oppgi din nåværende avleste kroppstemperatur (med ett desimaltall): "))
if temp < 36.5:
    print("Din kroppstemperatur er lavere enn normalen.")
elif temp >= 36.5 and temp <= 37.5:
    print("Din kroppstemperatur er innenfor normalen.")
else:
    print("Du har feber.")

#6
priser = [20,15,40,12]
antall = [int(input("Hvor mange brød vil du ha? ")),int(input("Hvor mange melk vil du ha? ")),
          int(input("Hvor mange ost vil du ha? ")),int(input("Hvor mange yoghurt vil du ha? "))]
totalpris = priser[0]*antall[0] + priser[1]*antall[1] + priser[2]*antall[2] + priser[3]*antall[3]
print("Totalprisen blir",str(totalpris)+".")

#Nye priser på brød og yoghurt:
priser[0]=40

#Uke 3-oppgaver Trix
#1
maaneder = ["Januar","Februar","Mars","April","Mai","Juni","Juli","August","September","Oktober","November","Desember"]
userinput = int(input("Oppgi et heltall mellom 1 og 12: "))
if userinput not in [1,12]:
    print("Tallet du har oppgitt er ikke mellom 1 og 12")
else:         
    print("Dette tilsvarer",maaneder[userinput-1])

#2
from ezgraphics import GraphicsWindow
vindu = GraphicsWindow()
lerret = vindu.canvas()
x = int(input("Oppgi x-koordinatet: "))
y = int(input("Oppgi y-koordinatet: "))
lerret.drawOval(x-5,y-5,10,10)
vindu.wait()

win = GraphicsWindow(400,400)
#Kan foreløpig ikke se noe vindu...









