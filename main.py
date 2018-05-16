#!/usr/bin/python
import os, piecash, yaml, time, datetime, math, sys, calendar
from piecash import open_book, Transaction, Split, Account
from pprint import pprint
from io import StringIO

# simple account class
class account:

    def __init__(self,name, goal, budget, post_debt_budget, saving, balance):
        self.name = name
        self.goal = goal
        self.budget = budget
        self.post_debt_budget = post_debt_budget
        self.saving = saving 
        self.starting_balance = math.floor(balance)
        self.end_of_year_balance = 0
        self.balance = math.floor(balance)
        self.date = None
        self.iteration = 0

        self.goal_met = 0

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
            name=a['name'], goal=a['goal'], budget=a['budget'], 
            post_debt_budget=a['budgetpostdebt'], saving=True, 
            balance=book.accounts(fullname=a['name']).get_balance(False)))
        
    # for each debt accounts
    for a in budget_file['debt']['accounts']:
        accounts.append(account(
            name=a['name'], goal=a['goal'], budget=a['budget'], 
            post_debt_budget=0, saving=False,
            balance=book.accounts(fullname=a['name']).get_balance(False)))

    return accounts

def is_post_debt(accounts):
    for a in accounts:
        if not a.saving:
            if a.date is None:
                return False
    return True


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

# if pay_day is today, balances already affected
#    so jump ahead to next payday
if pay_day == datetime.date.today():
    pay_day+= datetime.timedelta(14)

first_pay_day = pay_day

iteration = 0
# for each friday for the rest of the year
while pay_day.year <= datetime.date.today().year+1:
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

        if a.saving:
           increment = (a.post_debt_budget if is_post_debt(accounts) else a.budget)* (1 if a.saving else -1)
        else:
           increment = (a.budget)* (1 if a.saving else -1)

        amount += increment

        amount = amount if amount > 0 else 0

        # if set date if goal met
        if a.date is None:
            if a.saving:
                if amount >= a.goal:
                    a.date = pay_day
                    a.iteration = iteration
                    a.goal_met = amount
            else:
                if amount == 0:
                    a.date = pay_day
                    a.iteration = iteration

        a.projection = amount

        a.balance = amount

        if(pay_day.year == datetime.date.today().year):
            last_pay_day_of_year = pay_day + datetime.timedelta(-14)
            a.end_of_year_balance = amount

        # print account amount for this date
        print(str(amount).ljust(5), end='')
        if amount > 0:
            print(' (' + ('+' if a.saving else '-'), end='')
            print((str(increment)+')').ljust(4), end='')
    print()

    # increment pay day
    pay_day += datetime.timedelta(14)



# year_iteration = iteration
largest_iteration = iteration

# if any account has not met goal
# project until goal is met
for a in accounts:
    temp_iteration = iteration
    while a.date is None:

        temp_iteration += 1    
        a.projection += (a.post_debt_budget if is_post_debt(accounts) else a.budget)*(1 if a.saving else -1)

        # if goal met
        if a.saving:
            if a.projection >= a.goal:
                a.date = pay_day  + datetime.timedelta(14*(temp_iteration-iteration))
                a.iteration = temp_iteration
                a.goal_met = a.projection
        else:
            if a.projection == 0:
                a.date = pay_day  + datetime.timedelta(14*(temp_iteration-iteration))
                a.iteration = temp_iteration
                a.goal_met = a.projection

        a.balance = a.projection

    # get largest iteration from today
    if temp_iteration > largest_iteration:
        largest_iteration = temp_iteration


print()
print("       - Goals Met - \n")

# print waaaay ahead per account
for a in accounts:
    print(a.date, end=' | ')
    print(str(a).ljust(16) , end=' ')
    print(str(a.goal_met).ljust(5), end =' | ')

    months = (a.date - first_pay_day).days/30

    if months < 12:
        print(round(months,1), end='')
        print(' months ahead', end='')
    else:
        print(round(months/12,1), end='')
        print(' years ahead',end='')

    print(" ("+str(a.iteration)+" paychecks)", end='')
    print(" ahead")

# reset standard out
sys.stdout = standard_out

# print today and future-most dates
print()
print("       - End of Year Projections - \n")
print(str(datetime.date.today()).rjust(33), end='')
print("       "+ str(last_pay_day_of_year))

net_start = 0
net_end = 0

# print account summaries
for a in accounts:
    print(str(a).ljust(15), end=' ')
    print('(+' if a.saving else '(-', end='')
    print(str(a.budget).ljust(3), end='')
    print(")", end='')
    print(" Balance: " + str(a.starting_balance).ljust(5), end='')

    # end_of_year_balance = a.balance+a.budget*iteration* (1 if a.saving else -1)
    # end_of_year_balance = end_of_year_balance if end_of_year_balance > 0 else 0
    print(" | Projection: " + str(a.end_of_year_balance).ljust(5), end='')

    # net_start = net_start + a.balance if a.saving else net_start - a.balance
    # net_end = net_end + end_of_year_balance if a.saving else net_end - end_of_year_balance

    net_start += a.starting_balance * (1 if a.saving else -1)
    net_end += a.end_of_year_balance * (1 if a.saving else -1)

    if a.saving and a.end_of_year_balance >= a.goal:
        # unending goal
        if a.goal == 0:
            print()
        # goal met with balance
        else:
            print(" Goal already met.", end='')

    print()


print(" ".ljust(27)+"Net: ",end='')
print(net_start, end='  |')
print(" ".ljust(8)+"Net: ",end='')
print(net_end, end='')

# print breakdown (prior standard output)
print()
print("       - Breakdown - \n")
print(result.getvalue())
print()
