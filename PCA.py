#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 20:42:10 2021

@author: hanworld
"""
import numpy as np
import numpy.matlib
from sklearn import datasets
import matplotlib.pyplot as plt

data = datasets.load_iris()
D = data['data']

####

sn, fn = D.shape #array的維度(sn:sample / fn:feature)
meanv = np.mean(D,axis=0) #axis=0 就是沿列計算
stdv = np.std(D,axis=0)
D2 = (D-np.matlib.repmat(meanv,sn,1))/np.matlib.repmat(stdv,sn,1)
C = np.dot(np.transpose(D2),D2)
EValue,Evector = np.linalg.eig(C)
#project matrix
PM1 = Evector[:,0:1]
PM2 = Evector[:,0:2]
PM3 = Evector[:,0:3]
#compressed data
CD1 = np.dot(D2,PM1)
CD2 = np.dot(D2,PM2)
CD3 = np.dot(D2,PM3)
#ratio
R = 1 - np.cumsum(EValue)/np.sum(EValue)
print("降至一維損失：",R[0])
print("降至二維損失：",R[1])
print("降至三維損失：",R[2])
x= np.zeros(150)
y= np.zeros(150)
for i in range(150):
    x[i] = CD2[i][0]
    y[i] = CD2[i][1]
plt.scatter(x[:50],y[:50],c="blue")
plt.scatter(x[50:100],y[50:100],c="red")
plt.scatter(x[100:],y[100:],c="green")








    
    
    