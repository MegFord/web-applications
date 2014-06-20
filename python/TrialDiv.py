#!/usr/bin/env python
import math
"""
Trial Division
"""
class Trial_Division:
    def find_primes(self, rt):
        primes = [2,3,5,7]
        for i in range(1,rt):
            if i != 1 and i%2 and i%3 and i%5 and i%7!= 0:
                primes.append(i)
        return primes 
     
    def div_primes(self, prime_factors, small_primes, b):
        for i in small_primes:
            if b%i == 0:
                b = b//i
                print b
                prime_factors.append(i)
            if b in small_primes:
                prime_factors.append(b)
                return prime_factors
        self.div_primes(prime_factors, small_primes, b)
        return prime_factors      
        
if __name__ == '__main__':
    tdv = Trial_Division()
    base_num = 636363
    with open('TrialDiv', 'w') as outfile:
        outfile.write('Prime factors of '+ str(base_num) + ':' + '\n')
        #calulate root of input num to find first value of b
        rt = int(math.ceil(math.sqrt(base_num)))
        print rt
        b = base_num
        prime_arr = []
        small_primes = tdv.find_primes(rt)
        prime_arr = tdv.div_primes(prime_arr, small_primes, b)
        for j in prime_arr:
            outfile.write(str(j) + '\t')
        outfile.write('\n')
        

