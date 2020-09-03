
#Trener pÃ¥ funksjoner

#Matematiske funksjoner

def togangern(a):
    tmp1=a
    verdi=2*tmp1
    return verdi

svar1=togangern(5)

def treukjente(x,y,z):
    tmp1, tmp2, tmp3 = x, y, z
    verdi=2*tmp1 + 3*tmp2 *2*tmp3
    return verdi

svar2=float(treukjente(1,2,3))

def toukjente(a,b):
    verdi=2*a + 2*b
    return verdi

svar3=int(toukjente(5,6))
svar3=str(toukjente(5,6))

liste1=[1,2,3,4,5,6,7,8,9]
liste2=[4,5,6,7]

def gjennomgang(a):
    for i in a:
        if i<=5:
            print("Tallet er lavt")
        else: print("Tallet er hÃ¸yt")
      
gjennomgang(liste1)
gjennomgang(liste2)

def gjennomgang2(a):
    a = 0
    for i in a:
        if i <= 5:
            print("Tallet er lavt")
        else: print("Tallet er hÃ¸yt")
        a = i + 1
        
gjennomgang2(0)

## Repetisjon 11.05.20

string1 = input("Oppgi et ord med små bokstaver: ")
string2 = input("Oppgi et annet ord med små bokstaver: ")
string3 = input("Oppgi et tredje og siste ord med små bokstaver: ")

def uppercase(string):
    result = string1.upper()
    return result

uppercase(string1)
uppercase(string2)














