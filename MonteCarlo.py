#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 11:02:21 2021

@author: hanworld
"""

import math
import scipy.stats
from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt

def blscall(S, K, T, r, vol):
    d1 = (math.log(S/K)+(r+vol*vol/2)*T)/(vol*math.sqrt(T))
    d2 = d1-vol*math.sqrt(T)
    call = S*norm.cdf(d1)-K*math.exp(-r*T)*norm.cdf(d2)
    return call


def MCcall(S, K, T, r, vol, N):
    dt = T/N
    St = np.zeros((N+1))
    St[0] = S
    for i in range(N):
        St[i+1] = St[i]*math.exp((r-0.5*vol*vol)*dt
                    +vol*np.random.normal()*math.sqrt(dt))
    return St

def BisectionBLS(S,K,T,r,call):
    left = 0.00000001
    right = 1
    while(right-left>0.00001):
        middle = (left+right)/2
        if((blscall(S,K,r,T,middle)-call)
                   *(blscall(S,K,r,T,left)-call)<0):
            right = middle
        else:
            left = middle
    return (left+right)/2

'''Question 1'''

S = 50
K = 40
T = 2
r = 0.08
vol = 0.2

'''(1)請先計算Black-Scholes公式解'''
print(blscall(S, K, T, r, vol))

'''(2)請用Monte Carlo Simulation計算(N=100, M=1000)'''
N = 100
M = 1000

call = 0

for i in range(M):
    Sa = MCcall(S, K, T, r, vol, N)
    plt.plot(Sa)
    if(Sa[-1]-K>0):
        call += Sa[-1]-K
print((call/M)*math.exp(-r*T))

'''(3)重複Monte Carlo Simulation 10次，計算其與公式解的誤差'''
N = 100
M = 10
v=np.zeros(M)

BLS = blscall(S, K, T, r, vol)

for i in range(M):
    Sa = MCcall(S, K, T, r, vol, N)
    plt.plot(Sa)
    v[i] = abs((Sa[-1]-K)-BLS)
print(scipy.stats.variation(v))
    
'''(3)驗證N跟M的值變動時，誤差如何跟著改變'''
BLS = blscall(S, K, T, r, vol)

N = 200
varM = np.zeros(100)
for j in range(1,101):
    M = j*10
    v = np.zeros(M)
    for i in range(M):
        Sa = MCcall(S, K, T, r, vol, N)
        v[i] = abs((Sa[-1]-K)-BLS)
    varM[j-1] = scipy.stats.variation(v)
plt.plot(varM)


M = 200
varN = np.zeros(100)
for j in range(1,101):
    N = j*10
    v = np.zeros(M)
    for i in range(M):
        Sa = MCcall(S, K, T, r, vol, N)
        v[i] = abs((Sa[-1]-K)-BLS)
    varN[j-1] = scipy.stats.variation(v)
plt.plot(varN)

'''Question 2'''
'''驗證是否有volatility smile的現象(x:K, y:volatility)'''
S = 16393.16
K = np.zeros(17)
T = 14/365
r = 0.825/100
call = [655,585,499,434,372,306,248,199,156,
        117,86,60,41,28.5,20.5,14.5,10]
vol = np.zeros(17)
for i in range(17):
    K[i] = (15800+i*100)
    vol[i] = BisectionBLS(S, K[i], T, r, call[i])
plt.plot(K,vol)
plt.xlabel("K")
plt.ylabel("vol")










