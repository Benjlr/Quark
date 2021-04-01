
from Cointegration import prepare_data_coint_test
import numpy as np
import pandas
from helpers import MakeIntoDF, SaveIBDataToFile, clean
from ib_insync.contract import Stock
from Trade import Trader
from datetime import datetime, timedelta
from scipy import signal
from sklearn.decomposition import FastICA, PCA
import pywt
import matplotlib.pyplot as plt
import yfinance as yf  


etfs = [
    'EEM', 
    'EFA', 'EWA', 'EWC', 'EWJ', 
        'EWZ', 'FAS', 'FAZ', 'FXI', 'GDX', 
        'GLD', 'IGE', 'IWM', 'IYR', 'QID', 
        'QQQ', 'SDS', 'SKF', 'SPY', 'SSO', 
        'TZA', 'UNG', 'USO', 'VWO', 'XLE',
        'XLF', 'XLI', 'XRT' ]

#from the year of 2013–2015
'''
app = Trader()
for i in etfs:
    myContract = Stock(i, exchange='SMART', currency='USD')
    theStock = app.RetrieveHistoricalData(
            myContract, 
            endDate= '20151231 23:59:59', #YYYYMMDD{SPACE}hh:mm:ss[{SPACE}TMZ]'.
            duration= '3 y', 
            barsize= '1 day')
    theStock = MakeIntoDF(theStock)
    #theStock = clean(theStock)
    SaveIBDataToFile(theStock, i)
'''

def wave_smooth(data,nlevels,wv='db4'):
    n = (len(data)//2**nlevels)*2**nlevels
    data = data[-n:]
    
    coeffs = pywt.wavedec(data,wv,level=nlevels)
    for i in range(1,len(coeffs)):
        tmp = coeffs[i]
        mu,sigma,omega = tmp.mean(),tmp.std(),abs(tmp).max()
        kappa = (omega-mu)/sigma
        coeffs[i] = pywt.threshold(tmp,kappa,'garrote')
    
    rs = pywt.waverec(coeffs,wv)    
    return(rs)


def create_spectrum(rs):
    scales = np.arange(1,len(rs)+1)
    img = pywt.cwt(rs,scales,'morl')[0]
    return img

def MakeStationary(series, log_stationary=False):
    if log_stationary:
        series=np.log10(series)

    s1 = pandas.Series(series).pct_change().values[1:].reshape(-1,1)
    s1 = s1-(sum(s1)/len(s1))
    s1 = (s1/max(s1,key=abs))
    return s1

def GetRHD(observed, source):
    myRHD =0
    for i in range(0, len(observed)-1):
        myRHD += (RHD(observed[i+1], observed[i]) - RHD(source[i+1], source[i]))**2
    return (1/(len(observed)-1))*myRHD
    

def RHD(tOne, t):
    if tOne - t > 0:
        return 1
    elif tOne - t < 0:
        return -1
    else :
        return 0

completeSeries = np.empty(756)

for etf in etfs:
    #XXfile = prepare_data_coint_test(f"C:\\MyArea\\Repos\\Documents\\Quark\\testdata\\ETFs\\{etf}.csv")
    XXfile = yf.download(etf,'2013-01-01','2016-01-01')
    
    rs = wave_smooth(XXfile['Adj Close'],5)
    rs = np.insert(rs,0, np.zeros(len(XXfile['Adj Close']) - len(rs)))
    sub_array=[j-i for i, j in zip(rs[:-1], rs[1:])] 
    sub_array= np.insert(sub_array, 0,0)
    zero_crossings = np.where(np.diff(np.signbit(sub_array)))[0]
    zero_crossings=np.delete(zero_crossings,0)
    signals =np.zeros(len(rs))

    for i in range(0,len(sub_array)):
        if i-1 in zero_crossings:
            if sub_array[i] > 0:
                signals[i]=-1
            else:
                signals[i]=1

    lastIndex =-1    
    returns =np.zeros(len(signals)-1)
    opens = np.array(XXfile['Adj Close'])
    returns[0]=1000

    for i in range(1,len(signals)-1):
        if signals[i] != 0:
            if lastIndex == -1:
                returns[i] = returns[i-1]
                lastIndex = i
            elif signals[i] > 0:
                returns[i] = ((opens[i+1] / opens[lastIndex+1]) -1)*returns[i-1] + returns[i-1]
                lastIndex = i
            elif signals[i] < 0:
                returns[i] =(1- (opens[i+1] / opens[lastIndex+1]))*returns[i-1] + returns[i-1]
                lastIndex = i
        else:
            returns[i] = returns[i-1]

    #stionarySeries = MakeStationary(opens)
    stionarySeries = opens
    completeSeries = np.c_[completeSeries,stionarySeries ]

completeSeries = np.delete(completeSeries,0,1 )
ica = FastICA(whiten=True)
S_ = ica.fit_transform(completeSeries)  # Reconstruct signals
A_ = ica.mixing_  # Get estimated mixing matrix

etfCounter =0
for etf in etfs:
    XXfile = yf.download(etf,'2013-01-01','2016-01-01')
    realSeries = np.array(XXfile['Adj Close'])
    #realSeries = MakeStationary(realSeries)
    new_S_ = S_
    new_A_ = A_

    counter = 0
    while counter < 1:
        maxVal =0
        myRHD =0
        toremove=-1

        for i in range(0, len(new_S_[etfCounter])):
            source = np.dot(new_S_[:,i:i+1], new_A_.T[i:i+1,:])[:,etfCounter]
            myRHD = GetRHD(realSeries,source)
            if myRHD > maxVal:
                maxVal = myRHD
                toremove=i
        print(f"removing {toremove} with Q: {maxVal}")
        new_S_=np.delete(new_S_,toremove, axis=1)
        new_A_=np.delete(new_A_,toremove, axis=1)
        counter+=1

    plt.plot(np.dot(new_S_, new_A_.T)[:,etfCounter] + ica.mean_[etfCounter])
    #plt.plot(np.dot(S_, A_.T)[:,etfCounter] )
    plt.plot(realSeries, color='Red')
    plt.show()
    etfCounter+=1
    #for i in range(etfCounter, len(S_[etfCounter])):
    #   source = np.dot(S_[:,i:i+1], A_.T[i:i+1,:])[:,etfCounter]
    #   plt.plot(source)



