#!/usr/bin/env python
"""
sieve of Eratosthenes
"""
with open('Eratosthenes', 'w') as outfile:
    outfile.write('Integers from 1 to 120:' + '\n')
    for i in range(1,121):
        outfile.write(str(i) + '\t')
    outfile.write('\n')
    
    outfile.write('Remove 1:' + '\n')        
    for i in range(1,121):
        if i != 1:
           outfile.write(str(i) + '\t')
    outfile.write('\n')
           
    outfile.write('Remove multiples of 2:' + '\n')
    for i in range(1,121):
        if i == 2:
            outfile.write(str(i) + '\t') 
        elif i != 1 and i%2 != 0:
           outfile.write(str(i) + '\t') 
    outfile.write('\n')
           
    outfile.write('Remove multiples of 3:'+ '\n')
    for i in range(1,121):
        if i == 2 or i == 3:
            outfile.write(str(i) + '\t') 
        elif  i != 1 and i%2 and i%3 != 0:
           outfile.write(str(i) + '\t')
    outfile.write('\n')
    
    outfile.write('Remove multiples of 5:' + '\n') 
    for i in range(1,121):
        if i == 2 or i == 3 or i == 5:
            outfile.write(str(i) + '\t') 
        elif i != 1 and i%2 and i%3 and i%5!= 0:
           outfile.write(str(i) + '\t')
    outfile.write('\n')        
    
    outfile.write('Remove multiples of 7:' + '\n')
    for i in range(1,121):
        if i == 2 or i == 3 or i == 5 or i == 7:
            outfile.write(str(i) + '\t') 
        elif i != 1 and i%2 and i%3 and i%5 and i%7 != 0:
           outfile.write(str(i) + '\t')



