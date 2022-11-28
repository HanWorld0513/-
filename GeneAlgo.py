#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 14:05:34 2021

@author: hanworld
"""

#LPPL
#這裡的data就是p[0],p[1].....
#B： increase rate
#tc：泡沫爆掉的時間
#t：現在的時間
#利用cos波去控制週期
#omega：控制距離爆掉的時候波動會變密多少
#每一個gene會有對應的tc, beta, omega, phi
#A,B,C 會因應上面四組參數而生
import numpy as np
import matplotlib.pyplot as plt

def MAE(real, predict):
    print('MAE =',np.mean(abs(real[:len(predict)]  - predict)))

def lppl(t, A, B, tc, beta, C, omega, phi):
    return A + (B*((tc-t)**beta))*(1+C*np.cos((omega*np.log(tc-t)+phi)))

def gene2coef(gene):
    tc = np.sum(2**np.arange(4)*gene[0:4])+500
    beta = np.sum(2**np.arange(11)*gene[4:15])/2047
    #omega 範圍怎麼訂？
    omega = np.sum(2**np.arange(5)*gene[15:20])
    phi = np.pi*(np.sum(2**np.arange(10)*gene[20:30])+1024)/2047
    return tc, beta, omega, phi

# tc in [500,515][bit = 4]
# 0 < beta < 1 [bit = 11]
# omega [4,35],bit = 5
# 0 < phi < 2*np.pi[bit = 11]

# A > 0
# B < 0
# C != 0 [-1,1]

T =np.zeros(600)
for t in range(600):
    T[t] = t

#參考真實data: p
p = np.load('data.npy')
#時間序列t=[0,......,599]

plt.plot(T,p)

N = 5000 #人口數量
G = 3 #世代數
Bit = 30
survive_rate = 0.001 #存活率
mutation_rate = 0.0001
survive = round(N*survive_rate) #多少人會活下來
mutation = round(N*Bit*mutation_rate) #多少基因會突變
pop = np.random.randint(0,2,(N,Bit)) #所有的人們
fit = np.zeros((N,1))

for generation in range(G):
    print("Generation: ",generation)
    for i in range(N):
        tc, beta, omega, phi = gene2coef(pop[i,:])
        #ax=b
        a = np.zeros((600,3)) #600x3 array
        b = np.zeros((600,1)) #600x1 array
        for t in range(tc):
            b[t] = np.log(p[t])
            a[t,0] = 1
            a[t,1] = (tc-t)**beta
            a[t,2] = ((tc-t)**beta)*np.cos(omega*np.log(tc-t)+phi)
        #x=[A,B,BC]
        x = np.linalg.lstsq(a,b,rcond=None)[0]
        A = x[0]
        B = x[1]
        C = x[2]/x[1]
        fit[i] = np.mean(abs(lppl(T[0:tc], A, B, tc, beta, C, omega, phi)-np.log(p[0:tc])))#越小越適合活著
    sortf = np.argsort(fit[:,0]) #從小到大排序
    pop = pop[sortf,:]
    for i in range(survive,N): #從活下來的人裡面隨機找人交配
        fid = np.random.randint(0,survive) #father id
        mid = np.random.randint(0,survive) #mother id
        while(fid==mid):
            mid = np.random.randint(0,survive)
        mask = np.random.randint(0,2,(1,Bit)) #1xBit矩陣遮罩，裡面都是0或1
        son = pop[mid,:].copy()
        father = pop[fid,:]
        son[mask[0,:]==1] = father[mask[0,:]==1]#把爸爸基因copy過來
        pop[i,:] = son
    for i in range(mutation):
        m = np.random.randint(0,N)
        n = np.random.randint(0,Bit)
        pop[m,n] = 1-pop[m,n] #0->1,1->0
    ############
    p2 = np.zeros(tc)
    for t in range(tc):
        p2[t] = np.exp(lppl(t,A,B,tc,beta,C,omega,phi))

    T2 = np.zeros(tc)
    for t in range(tc):
        T2[t] = t
    MAE(p,p2)
print("Generation ended.")

for i in range(N):
    tc, beta, omega, phi = gene2coef(pop[i,:])
    fit[i] = np.mean(abs(lppl(T[0:tc], A, B, tc, beta, C, omega, phi)-np.log(p[0:tc])))
sortf = np.argsort(fit[:,0])
pop = pop[sortf,:]

tc, beta, omega, phi = gene2coef(pop[0,:])
for t in range(tc):
    b[t] = np.log(p[t])
    a[t,0] = 1
    a[t,1] = (tc-t)**beta
    a[t,2] = ((tc-t)**beta)*np.cos(omega*np.log(tc-t)+phi)
#x=[A,B,BC]
x = np.linalg.lstsq(a,b,rcond=None)[0]
A = x[0]
B = x[1]
C = x[2]/x[1]

print('tc =', tc)
print('beta =', beta)
print('omega =', omega)
print('phi =', phi)
print('A =', A)
print('B =', B)
print('C =', C)

p2 = np.zeros(tc)
for t in range(tc):
    p2[t] = np.exp(lppl(t,A,B,tc,beta,C,omega,phi))

T2 = np.zeros(tc)
for t in range(tc):
    T2[t] = t

plt.plot(T2,p2)
MAE(p,p2)



