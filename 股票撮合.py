#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 22:12:18 2021

@author: hanworld
"""

T = int(input("總共有幾筆測資： "))
for t in range(T):
    N = int(input("總共有幾筆交易： "))
    #初始化變數
    buy = [] #委買
    sell = [] #委賣
    stockprice = -1 #成交價格
    for n in range(N):
        tmp = input("請輸入買賣單： ") #buy/sell __ shares at __
        strlist = tmp.split(' ') #將字串變成list
        share = int(strlist[1])  #欲交易股數
        price = int(strlist[-1]) #欲交易價錢
        '''欲買股票'''
        if strlist[0] in ["buy", "b"]:  #純粹是我懶得打完buy
            while len(sell) > 0:
                order = sell[0]  #賣的最低價
                if order[0] > price: #出的錢不夠多
                    break #不成交
                #反之成交
                dealamount = min(order[1], share) #成交量為委賣和欲買的最小值
                stockprice = order[0] #成交價 = 賣方出價
                order[1] -= dealamount #委賣數量扣掉成交量
                share -= dealamount    #欲買數量扣掉成交量
                if order[1] == 0: #委賣最低價已售空
                    del sell[0] 
                if share == 0:    #欲買量已買完
                    break
            if share > 0: #如果還沒買夠or沒買到，回去排隊
                i = 0 
                while i < len(buy) and price < buy[i][0]: #insert插入
                    i += 1
                if i < len(buy) and price == buy[i][0]: #欲買價和委買價相同
                    buy[i][1] += share #只需要加數量
                else: #新增一筆委買
                    buy.insert(i, [price, share])
            #print('sell = ', sell)
            #print('buy =  ', buy)
            #print('stockprice = ', stockprice)
            
        '''欲賣股票'''
        if strlist[0] in ["sell", "s"]:  #純粹是我懶得打完sell
            while len(buy) > 0:
                order = buy[0]  #買的最高價
                if order[0] < price: #賣太貴
                    break #不成交
                #反之成交
                dealamount = min(order[1], share) #成交量為委買和欲賣的最小值
                stockprice = price #成交價 = 賣方出價
                order[1] -= dealamount #委買數量扣掉成交量
                share -= dealamount    #欲賣數量扣掉成交量
                if order[1] == 0: #委買最高價已買完
                    del buy[0] 
                if share == 0:    #欲賣量已賣完
                    break
            if share > 0: #如果還沒賣夠or沒賣到，回去排隊
                i = 0 
                while i < len(sell) and price > sell[i][0]: #insert插入
                    i += 1
                if i < len(sell) and price == sell[i][0]: #欲賣價和委賣價相同
                    sell[i][1] += share #只需要加數量
                else: #新增一筆委賣
                    sell.insert(i, [price, share])  
            #print('sell = ', sell)
            #print('buy =  ', buy)
            #print('stockprice = ', stockprice)
        '''更新交易狀況'''
        #賣的最低價
        if len(sell) == 0:
            print('-',end = ' ')
        else:
            print(sell[0][0], end = ' ')
        #買的最高價
        if len(buy) == 0:
            print('-', end = ' ')
        else:
            print(buy[0][0], end = ' ')
        #成交價
        if stockprice == -1:
            print('-')
        else:
            print(stockprice)