#!/usr/bin/env python3

from selenium import webdriver
from time import sleep
import pandas as pd
import numpy as np

chromedriver = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
browser = webdriver.Chrome(chromedriver)
browser.get('https://tip.railway.gov.tw/tra-tip-web/tip?lang=EN_US')
browser.find_element_by_id('startStation').send_keys('1040-Shulin')
browser.find_element_by_id('endStation').send_keys('7000-Hualien')
browser.find_element_by_id('rideDate').send_keys('2022/06/03')
browser.find_element_by_id('startTime').send_keys('06:00')
browser.find_element_by_id('endTime').send_keys('18:00')
sleep(1)
browser.find_element_by_xpath('//*[@id="queryForm"]/div[6]/input').click()

info = []
for i in range(20):
	place = 2*(i+1)
	temp=[]
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[1]/ul/li/a'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[1]/ul/li/span[3]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[1]/ul/li/span[5]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[2]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[3]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[4]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[5]'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[7]/span'%place).text)
	temp.append(browser.find_element_by_xpath('//*[@id="pageContent"]/div/table/tbody/tr[%d]/td[8]/span'%place).text)
	info.append(temp)
info_pd = pd.DataFrame(info)
info_pd.columns=['Train type and code','Originating Station','Terminal Station','Departure time','Arrival time',
				'Travel time','Via','Adult','Discount']
info_pd.index=np.arange(1, 21)

info_pd.to_csv('railway.csv')