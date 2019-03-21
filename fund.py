
# coding: utf-8

# In[45]:


import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import pickle
import os
# 基金列表網址
urlList = "https://www.sitca.org.tw/ROC/Industry/IN2421.aspx"
# 基金明細網址
urlFund = "https://www.sitca.org.tw/ROC/Industry/IN2422.aspx"
# 瀏覽器Head
url_headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}

# 回傳基金清單
# 參數txtYear: 年度
# 參數txtMonth: 月份
def getFund_List(txtYear="2019", txtMonth="01"):
    url_params = {"txtYEAR":txtYear, "txtMONTH":txtMonth}
    r = requests.get(urlList, headers = url_headers, params = url_params)
    r.encoding = "utf8"
    df = []
    if(r.status_code == 200):
        soup = BeautifulSoup(r.text, "lxml")
        # 取出html tag為tr, 且css為DTeven及DTodd
        trs = soup.find_all("tr", attrs={"class":["DTeven","DTodd"]})
        pattern = "EUCA\w+"   # 正則表示式
        columnName = ['基金代號','基金名稱','1個月','3個月','6個月','1年','2年','3年','5年','累計','十年','年化標準差','Sharpe']
        if (len(trs) > 0):
            for tr in trs:
                tds = tr.find_all("td")
                tmp=[]
                for idx in range(len(tds)):
                    if(idx == 0):
                        # 用正則表示式, 取出基金代號
                        tmp.append(re.findall(pattern, tds[idx].a["href"])[0])
                    if(tds[idx].string.strip()==''):
                        tmp.append(np.nan)
                    elif(idx < 3):                        
                        tmp.append(tds[idx].string.strip())
                    else:
                        tmp.append(float(tds[idx].string.strip()))
                df.append(tmp)
            df = pd.DataFrame(df, columns = columnName)
            # 將字串轉為數值
            '''
            df['1個月'] = pd.to_numeric(df['1個月'])
            df['3個月'] = pd.to_numeric(df['3個月'])
            df['6個月'] = pd.to_numeric(df['6個月'])
            df['1年'] = pd.to_numeric(df['1年'])
            df['2年'] = pd.to_numeric(df['2年'])
            df['3年'] = pd.to_numeric(df['3年'])
            df['5年'] = pd.to_numeric(df['1個月'])
            df['累計'] = pd.to_numeric(df['累計'])
            df['十年'] = pd.to_numeric(df['十年'])
            df['年化標準差'] = pd.to_numeric(df['年化標準差'])
            df['Sharpe'] = pd.to_numeric(df['Sharpe'])
            '''
        else:
            print("Year="+txtYear+", Month="+txtMonth+", 無資料回傳; 請檢查條件是否正確....")
    else:
        print("Status_code="+r.status_code+", 請檢查網頁是否異常....")
        print("網址:" + urlList)
    return df

# 回傳基金類別明細
def getFund(txtYEAR="2019",txtMONTH="01",txtGROUPID="EUCA000500"):
    url_params = {'txtYEAR':txtYEAR, 'txtMONTH':txtMONTH, 'txtGROUPID':txtGROUPID}
    columnName = ['基金名稱','基金英文名','1個月','3個月','6個月','1年','2年','3年','5年','累計','十年','年化標準差','Sharpe']
    df = []
    r = requests.get(urlFund, headers = url_headers, params = url_params)
    r.encoding = "utf8"
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text, "lxml")
        trs = soup.find_all("tr", attrs={"class":["DTeven","DTodd"]})
        if(len(trs)>0):
            for tr in trs:
                tds = tr.find_all("td")
                tmp = []
                for idx in range(1, len(tds)):
                    if(tds[idx].string.strip()==''):
                        tmp.append(np.nan)
                    elif(idx < 3):
                        tmp.append(tds[idx].string.strip())
                    else:
                        tmp.append(float(tds[idx].string.strip()))
                df.append(tmp)
            df = pd.DataFrame(df, columns = columnName)
            '''
            df['1個月'] = pd.to_numeric(df['1個月'])
            df['3個月'] = pd.to_numeric(df['3個月'])
            df['6個月'] = pd.to_numeric(df['6個月'])
            df['1年'] = pd.to_numeric(df['1年'])
            df['2年'] = pd.to_numeric(df['2年'])
            df['3年'] = pd.to_numeric(df['3年'])
            df['5年'] = pd.to_numeric(df['1個月'])
            df['累計'] = pd.to_numeric(df['累計'])
            df['十年'] = pd.to_numeric(df['十年'])
            df['年化標準差'] = pd.to_numeric(df['年化標準差'])
            df['Sharpe'] = pd.to_numeric(df['Sharpe'])
            '''
        else:
            print("無資料, 請檢查查詢條件.....")
    else:
        print("Status_code=" + r.status_code+", 網頁查詢錯誤....")
    return df

# 策略4433
'''
四四三三法
台大教授邱顯比、李存修共同研製
四:1年績效在同類型基金前1/4
四:2年、3年、5年和今年以來績效在同類型基金前1/4
三:6個月績效排名在同類型基金前1/3
三:3個月績效排名在同類型基金前1/3
'''
def Strategy4433(df):
    cnt = df.shape[0]
    cnt4 = int(cnt/4)
    cnt3 = int(cnt/3)
    Y1 = df.sort_values(by=['1年'],ascending=False).head(cnt4)
    Y2 = df.sort_values(by=['2年'],ascending=False).head(cnt4)
    Y3 = df.sort_values(by=['3年'],ascending=False).head(cnt4)
    Y5 = df.sort_values(by=['5年'],ascending=False).head(cnt4)
    YY = df.sort_values(by=['累計'],ascending=False).head(cnt4)
    M3 = df.sort_values(by=['3個月'],ascending=False).head(cnt3)
    M6 = df.sort_values(by=['6個月'],ascending=False).head(cnt3)
    
    fund = set(Y1['基金名稱']).intersection(set(Y2['基金名稱'])).intersection(set(Y3['基金名稱'])).intersection(set(YY['基金名稱'])).intersection(set(M3['基金名稱'])).intersection(set(M6['基金名稱']))
    fund = list(fund)
    return Y1[Y1.基金名稱.isin(fund)]
    
# 策略222
'''
基金教母蕭碧燕
短期(6個月)、中期(1年)、長期(3年)績效都排在前1/2
'''
def Strategy222(df):
    cnt = df.shape[0]
    cnt2 = int(cnt/2)
    M6 = df.sort_values(by=['6個月'],ascending=False).head(cnt2)
    Y1 = df.sort_values(by=['1年'],ascending=False).head(cnt2)
    Y3 = df.sort_values(by=['3年'],ascending=False).head(cnt2)
    fund = list(set(M6['基金名稱']).intersection(set(Y1['基金名稱'])).intersection(set(Y3['基金名稱'])))
    fund
    return Y1[Y1.基金名稱.isin(fund)]

# 序列化
def serialization(df, fileName="fund.pickle"):
    # 判斷檔案是否存在, 有則先移除
    if os.path.exists(fileName):
        os.remove(fileName)
    fo = open(fileName, 'wb')
    pickle.dump(df, fo)
    fo.close()
    print("序列化完成, 檔案:" + fileName)


# 反序列化
def deserialization(fileName="fund.pickle"):
    # 判斷檔案是否存在
    if os.path.exists(fileName):
        fi = open(fileName, 'rb')
        data = pickle.load(fi)
        return data
    else:
        print("檔案:"+fileName+", 不存在.....")
    
if __name__=="__main__":
    funds = getFund_List("2019", "01")
    print(funds)

