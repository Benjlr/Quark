
from Cointegration import prepare_data_coint_test
import numpy as np
import pandas
from helpers import MakeIntoDF, SaveIBDataToFile, clean
from ib_insync.contract import Stock
from Trade import Trader
from datetime import datetime, timedelta
from scipy import signal
from sklearn.decomposition import FastICA, PCA
import matplotlib.pyplot as plt
import yfinance as yf  
from wavelet_funcs import *
from sklearn import svm


completeSeries = np.empty(756)

XXfile = yf.download('EWA','2013-01-01','2016-01-01')
opens = np.array(XXfile['Adj Close'])
#stionarySeries = MakeStationary(opens)
stionarySeries = opens
completeSeries = np.c_[completeSeries,stionarySeries ]


for i in range(0,10):
    completeSeries = np.c_[completeSeries,np.empty(756) ]


completeSeries = np.delete(completeSeries,0,1)

ica = FastICA(whiten=False)
S_ = ica.fit_transform(completeSeries)  # Reconstruct signals
A_ = ica.mixing_  # Get estimated mixing matrix


etfCounter =0
XXfile = yf.download(etf,'2013-01-01','2016-01-01')
realSeries = np.array(XXfile['Adj Close'])
#realSeries = MakeStationary(realSeries)
my_S_ =S_
my_A_=A_
counter = 0
while counter < 1:
    minVal =99
    myRHD =0
    toremoveMin=-1

    for i in range(0, len(my_S_[etfCounter])):
        new_S_=np.delete(my_S_,i, axis=1)
        new_A_=np.delete(my_A_,i, axis=1)
        source = np.dot(new_S_, new_A_.T)[:,etfCounter]
        myRHD = GetRHD(realSeries,source)
        if myRHD < minVal:
            minVal = myRHD
            toremoveMin=i
    print(f"removing {toremoveMin} with Q: {minVal}")
    plt.plot(np.dot(new_S_[:,toremoveMin:toremoveMin+1], new_A_.T[toremoveMin:toremoveMin+1,:])[:,etfCounter], color ='Orange')
    plt.plot(realSeries-(sum(realSeries)/len(realSeries)), color='Red')
    plt.show()
    my_S_=np.delete(my_S_,toremoveMin, axis=1)
    my_A_=np.delete(my_A_,toremoveMin, axis=1)
    counter+=1

plt.plot(np.dot(my_S_, my_A_.T)[:,etfCounter] + ica.mean_[etfCounter])
#plt.plot(np.dot(S_, A_.T)[:,etfCounter] )
plt.plot(realSeries, color='Red')
plt.show()
etfCounter+=1