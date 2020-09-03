first = input("Enter your first name: ")
second = input("Enter your significant other's first name: ")

initials = first[0]+"&"+second[0]
print(initials)

bottles = int(input("How many bottles? "))
unitprice = float(input("What is the price per bottle? "))
totalprice = bottles*unitprice
print("The total price is", totalprice)

#Formatted output

price = 1.2195786
print("%f" % price)

# "How To 2.1" (p. 53)

# Defining constants:
PENNIES_PER_DOLLAR = 100
PENNIES_PER_QUARTER = 25

# Obtaining user input:
userInput = input("Enter bill value (1 = $1, 5 = $5 etc.): ")
billValue = int(userInput)
userInput = input("Enter item price in pennies: ")
itemPrice = int(userInput)

# Computing change due:
changeDue = billValue*PENNIES_PER_DOLLAR - itemPrice
dollarCoins = changeDue // PENNIES_PER_DOLLAR
changeDue = changeDue % PENNIES_PER_DOLLAR
quarterCoins = changeDue // PENNIES_PER_QUARTER

# Print output:
print("%16d" % dollarCoins)
print("%16d" % quarterCoins)

