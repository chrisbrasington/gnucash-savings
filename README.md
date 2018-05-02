#gnucash-saver
settings.yaml file:
```
file : './file.gnucash'

savings:
    accounts: 
        - name: 'Assets:Current Assets:Savings Account:Camper'
          goal: 10000
          budget: 200

debt:
    accounts: 
        - name: 'Liabilities:Loans:Car Loan' 
          goal: 0
          budget: 350
```
Note: Projections use starting balance of known accounts.
./main.py output:
```
2018-05-11 |  Camper 200   |  Car Loan 3797 
2018-05-25 |  Camper 400   |  Car Loan 3447 
2018-06-08 |  Camper 600   |  Car Loan 3097 
2018-06-22 |  Camper 800   |  Car Loan 2747 
2018-07-06 |  Camper 1000  |  Car Loan 2397 
2018-07-20 |  Camper 1200  |  Car Loan 2047 
2018-08-03 |  Camper 1400  |  Car Loan 1697 
2018-08-17 |  Camper 1600  |  Car Loan 1347 
2018-08-31 |  Camper 1800  |  Car Loan 997  
2018-09-14 |  Camper 2000  |  Car Loan 647  
2018-09-28 |  Camper 2200  |  Car Loan 297  
2018-10-12 |  Camper 2400  |  Car Loan 0    
2018-10-26 |  Camper 2600  |  Car Loan 0    
2018-11-09 |  Camper 2800  |  Car Loan 0    
2018-11-23 |  Camper 3000  |  Car Loan 0    
2018-12-07 |  Camper 3200  |  Car Loan 0    
2018-12-21 |  Camper 3400  |  Car Loan 0    

[... 1.9 years ahead (50 paychecks) ahead ...]
2020-04-10 |  Camper 10000 |  Car Loan 0

                    2018-05-11       2018-12-21
Camper          (+) Balance: 0     | Projection: 10000 | 2020-04-10 GOAL MET
Car Loan        (-) Balance: 4147  | Projection: 0     | 2018-10-12 GOAL MET
```