# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 20:38:08 2021

@author: USER
"""

import numpy as np
import math
import matplotlib.pyplot as plt
npzfile = np.load('CBCL.npz')
trainface = npzfile['arr_0']
trainnonface = npzfile['arr_1']
testface = npzfile['arr_2']
testnonface = npzfile['arr_3']
# face1 = trainface[1500,:].reshape((19,19))
# plt.imshow(face1,cmap='gray')
trpn = trainface.shape[0]
trnn = trainnonface.shape[0]
tepn = testface.shape[0]
tenn = testnonface.shape[0]

ftable = []
for y in range(19):
    for x in range(19):
        for h in range(2,20):
            for w in range(2,20):
                if(y+h*1-1<=18 and x+w*2-1<=18):
                    ftable.append([0,y,x,h,w])
                if(y+h*2-1<=18 and x+w*1-1<=18):
                    ftable.append([1,y,x,h,w])
                if(y+h*1-1<=18 and x+w*3-1<=18):
                    ftable.append([2,y,x,h,w])
                if(y+h*2-1<=18 and x+w*2-1<=18):
                    ftable.append([3,y,x,h,w])
fn = len(ftable)

def fe(sample,ftable,c): #第c個特徵
    ftype,y,x,h,w = ftable[c]
    T = np.arange(361).reshape((19,19))#361是pixel數
    if ftype==0:#左-右
        output = np.sum(sample[:,T[y:y+h,x:x+w].flatten()],axis=1)-np.sum(sample[:,T[y:y+h,x+w:x+w*2].flatten()],axis=1)
    elif ftype==1:#下-上
        output = np.sum(sample[:,T[y+h:y+h*2,x:x+w].flatten()],axis=1)-np.sum(sample[:,T[y:y+h,x:x+w].flatten()],axis=1)
    elif ftype==2:#白-黑+白
        output = np.sum(sample[:,T[y:y+h,x:x+w].flatten()],axis=1)-np.sum(sample[:,T[y:y+h,x+w:x+w*2].flatten()],axis=1)+np.sum(sample[:,T[y:y+h,x+w*2:x+w*3].flatten()],axis=1)
    else:#左上-右上-左下+右下
        output = np.sum(sample[:,T[y:y+h,x:x+w].flatten()],axis=1)-np.sum(sample[:,T[y:y+h,x+w:x+w*2].flatten()],axis=1)-np.sum(sample[:,T[y+h:y+h*2,x:x+w].flatten()],axis=1)+np.sum(sample[:,T[y+h:y+h*2,x+w:x+w*2].flatten()],axis=1)  
    return output 

def WC(pw,nw,pf,nf): #弱分類
    maxf = max(pf.max(),nf.max())
    minf = min(pf.min(),nf.min())
    theta = (maxf-minf)/10+minf #第一刀在1/10的地方，threshold
    polarity = 1 #polarity預設為1
    #1 -->  (-)|(+)
    #0 -->  (+)|(-)
    #第一趟,假設最好一刀
    error = np.sum(pw[pf<theta])+np.sum(nw[nf>=theta])#分錯的部分
    if error>0.5:
        error = 1-error
        polarity = 0
    min_theta,min_error,min_polarity = theta,error,polarity
    #再試其他9刀
    for i in range(2,10):
        theta = (maxf-minf)*i/10+minf
        polarity = 1
        error = np.sum(pw[pf<theta])+np.sum(nw[nf>=theta])
        if error>0.5:
            error = 1-error
            polarity = 0
        if error<min_error:
            min_theta,min_error,min_polarity = theta,error,polarity
    return min_error,min_theta,min_polarity
        
##################################T = 1############################
print("T=1,start")
trpf = np.zeros((trpn,fn)) #training positive feature
trnf = np.zeros((trnn,fn)) #training negative feature
for c in range(fn):
    trpf[:,c] = fe(trainface,ftable,c)
    trnf[:,c] = fe(trainnonface,ftable,c)
pw = np.ones((trpn,1))/trpn/2
nw = np.ones((trnn,1))/trnn/2
SC = []
T = 1
for t in range(T):
    weightsum = np.sum(pw)+np.sum(nw)
    pw = pw/weightsum
    nw = nw/weightsum #normalize
    best_error,best_theta,best_polarity = WC(pw,nw,trpf[:,0],trnf[:,0])
    best_feature = 0#假設第0個最好
    #然後做剩下的
    for i in range(1,fn):
        error,theta,polarity = WC(pw,nw,trpf[:,i],trnf[:,i])
        if error<best_error:
            best_error,best_theta,best_polarity = error,theta,polarity
            best_feature = i
    beta = best_error / (1-best_error)
    alpha = math.log10(1/beta)
    SC.append([best_feature,best_theta,best_polarity,alpha])
    if best_polarity == 1: #分對的部分
        pw[trpf[:,best_feature]>=best_theta]*=beta
        nw[trnf[:,best_feature]<best_theta]*=beta
    else:
        pw[trpf[:,best_feature]<best_theta]*=beta
        nw[trnf[:,best_feature]>=best_theta]*=beta

#print('SC',SC)
print("T=1,half")
#算accuracy
trps = np.zeros((trpn,1))
trns = np.zeros((trnn,1))
alpha_sum = 0
for i in range(T):
    feature,theta,polarity,alpha = SC[i]
    if polarity == 1:#對了就加alpha分
        trps[trpf[:,feature]>=theta] += alpha
        trns[trnf[:,feature]>=theta] += alpha
    else:
        trps[trpf[:,feature]<theta] += alpha
        trns[trnf[:,feature]<theta] += alpha
    alpha_sum += alpha
trps = trps/alpha_sum
trns = trns/alpha_sum
#print(np.sum(trps>=0.5)/trpn) #TPR
#print(np.sum(trps<0.5)/trpn) 
#print(np.sum(trns>=0.5)/trnn) #FPR
#print(np.sum(trns<0.5)/trnn)  

########
#Q1: ROC Curve
Tc = np.zeros(100)
for i in range(100):
    Tc[i] = i/100
    
TPR = np.zeros(100)
FPR = np.zeros(100)

for i in range(100):
    a = 0
    b = 0
    for j in range(trpn):
        if trps[j][0]>=Tc[i]:
            a+=1
    for k in range(trnn):
        if trns[k][0]>=Tc[i]:
            b+=1
    TPR[i] = a/trpn
    FPR[i] = b/trnn

plt.plot(FPR, TPR, color='purple', label='ROC(T=1)')
print("T=1,done")
'''
plt.plot([0, 1], [0, 1], color='brown', linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
'''     
        
##################################T = 5############################
print("T=5,start")
trpf = np.zeros((trpn,fn)) #training positive feature
trnf = np.zeros((trnn,fn)) #training negative feature
for c in range(fn):
    trpf[:,c] = fe(trainface,ftable,c)
    trnf[:,c] = fe(trainnonface,ftable,c)
pw = np.ones((trpn,1))/trpn/2
nw = np.ones((trnn,1))/trnn/2
SC = []
T = 5
for t in range(T):
    weightsum = np.sum(pw)+np.sum(nw)
    pw = pw/weightsum
    nw = nw/weightsum #normalize
    best_error,best_theta,best_polarity = WC(pw,nw,trpf[:,0],trnf[:,0])
    best_feature = 0#假設第0個最好
    #然後做剩下的
    for i in range(1,fn):
        error,theta,polarity = WC(pw,nw,trpf[:,i],trnf[:,i])
        if error<best_error:
            best_error,best_theta,best_polarity = error,theta,polarity
            best_feature = i
    beta = best_error / (1-best_error)
    alpha = math.log10(1/beta)
    SC.append([best_feature,best_theta,best_polarity,alpha])
    if best_polarity == 1: #分對的部分
        pw[trpf[:,best_feature]>=best_theta]*=beta
        nw[trnf[:,best_feature]<best_theta]*=beta
    else:
        pw[trpf[:,best_feature]<best_theta]*=beta
        nw[trnf[:,best_feature]>=best_theta]*=beta

#print('SC',SC)
print("T=5,half")
#算accuracy
trps = np.zeros((trpn,1))
trns = np.zeros((trnn,1))
alpha_sum = 0
for i in range(T):
    feature,theta,polarity,alpha = SC[i]
    if polarity == 1:#對了就加alpha分
        trps[trpf[:,feature]>=theta] += alpha
        trns[trnf[:,feature]>=theta] += alpha
    else:
        trps[trpf[:,feature]<theta] += alpha
        trns[trnf[:,feature]<theta] += alpha
    alpha_sum += alpha
trps = trps/alpha_sum
trns = trns/alpha_sum

#Q1: ROC Curve
Tc = np.zeros(100)
for i in range(100):
    Tc[i] = i/100
    
TPR = np.zeros(100)
FPR = np.zeros(100)

for i in range(100):
    a = 0
    b = 0
    for j in range(trpn):
        if trps[j][0]>=Tc[i]:
            a+=1
    for k in range(trnn):
        if trns[k][0]>=Tc[i]:
            b+=1
    TPR[i] = a/trpn
    FPR[i] = b/trnn       
plt.plot(FPR, TPR, color='green', label='ROC(T=5)')
'''
plt.plot([0, 1], [0, 1], color='brown', linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
'''
print("T=5,done")
##################################T = 20############################
print("T=20,start")
trpf = np.zeros((trpn,fn)) #training positive feature
trnf = np.zeros((trnn,fn)) #training negative feature
for c in range(fn):
    trpf[:,c] = fe(trainface,ftable,c)
    trnf[:,c] = fe(trainnonface,ftable,c)
pw = np.ones((trpn,1))/trpn/2
nw = np.ones((trnn,1))/trnn/2
SC = []
T = 20
for t in range(T):
    weightsum = np.sum(pw)+np.sum(nw)
    pw = pw/weightsum
    nw = nw/weightsum #normalize
    best_error,best_theta,best_polarity = WC(pw,nw,trpf[:,0],trnf[:,0])
    best_feature = 0#假設第0個最好
    #然後做剩下的
    for i in range(1,fn):
        error,theta,polarity = WC(pw,nw,trpf[:,i],trnf[:,i])
        if error<best_error:
            best_error,best_theta,best_polarity = error,theta,polarity
            best_feature = i
    beta = best_error / (1-best_error)
    alpha = math.log10(1/beta)
    SC.append([best_feature,best_theta,best_polarity,alpha])
    if best_polarity == 1: #分對的部分
        pw[trpf[:,best_feature]>=best_theta]*=beta
        nw[trnf[:,best_feature]<best_theta]*=beta
    else:
        pw[trpf[:,best_feature]<best_theta]*=beta
        nw[trnf[:,best_feature]>=best_theta]*=beta

#print('SC',SC)
print("T=20,half")
#算accuracy
trps = np.zeros((trpn,1))
trns = np.zeros((trnn,1))
alpha_sum = 0
for i in range(T):
    feature,theta,polarity,alpha = SC[i]
    if polarity == 1:#對了就加alpha分
        trps[trpf[:,feature]>=theta] += alpha
        trns[trnf[:,feature]>=theta] += alpha
    else:
        trps[trpf[:,feature]<theta] += alpha
        trns[trnf[:,feature]<theta] += alpha
    alpha_sum += alpha
trps = trps/alpha_sum
trns = trns/alpha_sum

#Q1: ROC Curve
Tc = np.zeros(100)
for i in range(100):
    Tc[i] = i/100
    
TPR = np.zeros(100)
FPR = np.zeros(100)

for i in range(100):
    a = 0
    b = 0
    for j in range(trpn):
        if trps[j][0]>=Tc[i]:
            a+=1
    for k in range(trnn):
        if trns[k][0]>=Tc[i]:
            b+=1
    TPR[i] = a/trpn
    FPR[i] = b/trnn       
plt.plot(FPR, TPR, color='red', label='ROC(T=20)')      
plt.plot([0, 1], [0, 1], color='brown', linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()      
print("T=20,done")        
       
        
       
        
       
        
       
        
