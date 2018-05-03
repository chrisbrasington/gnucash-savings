#!/usr/bin/python
import os, piecash, yaml, time, datetime, math, sys, calendar
from piecash import open_book, Transaction, Split, Account
from pprint import pprint
from io import StringIO

# simple account class
class account:

    def __init__(self,name, goal, budget, saving, balance):
        self.name = name
        self.goal = goal
        self.budget = budget
        self.saving = saving 
        self.balance = math.floor(balance)
        self.date = None

    # account summary printout 
    def __str__(self):
        s = repr(self.name.split(':')[-1]).strip("'").ljust(6)
        # s += str(self.goal)
        # s += '\n'
        return s

def initialize():

    # settings file
    settings_file = 'settings.yaml'
    with open(settings_file) as ymlfile:
        budget_file = yaml.load(ymlfile)

    # book file path
    book_path = budget_file['file']

    # read book
    try:
        book = piecash.open_book(book_path, readonly=True, open_if_lock=True)
    except:
        print ('Unable to open database.')
        return
    accounts = []

    # for each savings account
    for a in budget_file['savings']['accounts']:
        accounts.append(account(
            name=a['name'], goal=a['goal'], budget=a['budget'], saving=True, 
            balance=book.accounts(fullname=a['name']).get_balance()))
        
    # for each debt accounts
    for a in budget_file['debt']['accounts']:
        accounts.append(account(
            name=a['name'], goal=a['goal'], budget=a['budget'], saving=False,
            balance=book.accounts(fullname=a['name']).get_balance()))

    return accounts

accounts = initialize()

# override standard out
standard_out = sys.stdout
result = StringIO()
sys.stdout = result

# get first friday of the year 
# use this as first payday of the year (probably inaccurate across years)
pay_day = datetime.date.today().replace(month=1, day=1)   

# count up to next friday
while pay_day.weekday() != 4:
    pay_day += datetime.timedelta(1)

# count up to this month
while(pay_day < datetime.date.today()):
    pay_day+= datetime.timedelta(14)

first_pay_day = pay_day

iteration = 0
# for each friday for the rest of the year
while pay_day.year <= datetime.date.today().year:
    # increment iteration
    iteration += 1

    # print pay day
    print(pay_day, end='')

    # for each accout
    for a in accounts:
        print(' | ', end=' ')
        print(a, end=' ')

        # increment amount
        amount = a.balance
        increment = a.budget*iteration* (1 if a.saving else -1)
        amount += increment

        amount = amount if amount > 0 else 0

        # if set date if goal met
        if a.date is None:
            if a.saving:
                if amount >= a.goal:
                    a.date = pay_day
            else:
                if amount == 0:
                    a.date = pay_day

        a.projection = amount

        # print account amount for this date
        print(str(amount).ljust(5), end='')
    print()

    # increment pay day
    pay_day += datetime.timedelta(14)

last_pay_day_of_year = pay_day + datetime.timedelta(-14)

# year_iteration = iteration
largest_iteration = iteration

# if any account has not met goal
# project until goal is met
for a in accounts:
    temp_iteration = iteration
    while a.date is None:

        temp_iteration += 1    
        a.projection += a.budget*(1 if a.saving else -1)

        # if goal met
        if a.saving:
            if a.projection >= a.goal:
                a.date = pay_day  + datetime.timedelta(14*(temp_iteration-iteration))
        else:
            if a.projection == 0:
                a.date = pay_day  + datetime.timedelta(14*(temp_iteration-iteration))

    # get largest iteration from today
    if temp_iteration > largest_iteration:
        largest_iteration = temp_iteration

print()
print('[... ', end='')

# print waaaay ahead
future_date = (first_pay_day + datetime.timedelta(14*largest_iteration))
months = (future_date - first_pay_day).days/30

if months < 12:
    print(months, end='')
    print(' months ahead', end='')
else:
    print(round(months/12,1), end='')
    print(' years ahead',end='')

print(" ("+str(largest_iteration)+" paychecks)", end='')
print(" ahead ...]")
print(future_date, end='')

for a in accounts:
    print(' | ', end=' ')
    print(a, end=' ')

    projection = a.balance + (a.budget * largest_iteration)*(1 if a.saving else -1)
    projection = projection if projection > 0 else 0
    print(projection, end='')

# reset standard out
sys.stdout = standard_out

# print today and future-most dates
print()
print("       - End of Year Projections - \n")
print(str(datetime.date.today()).rjust(33), end='')
print("       "+ str(last_pay_day_of_year))

# print account summaries
for a in accounts:
    print(str(a).ljust(15), end=' ')
    print('(+' if a.saving else '(-', end='')
    print(a.budget, end='')
    print(")", end='')
    print(" Balance: " + str(a.balance).ljust(5), end='')

    end_of_year_balance = a.balance+a.budget*iteration* (1 if a.saving else -1)
    end_of_year_balance = end_of_year_balance if end_of_year_balance > 0 else 0
    print(" | Projection: " + str(end_of_year_balance).ljust(5), end='')

    if a.saving and a.balance >= a.goal:
        # unending goal
        if a.goal == 0:
            print()
        # goal met with balance
        else:
            print("Goal already met.")

    print()

# print breakdown (prior standard output)
print()
print("       - Breakdown - \n")
print(result.getvalue())
print()