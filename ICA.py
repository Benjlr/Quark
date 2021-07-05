
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

completeSeries = np.empty(756)

for etf in etfs:
    XXfile = yf.download(etf,'2013-01-01','2016-01-01')
    opens = np.array(XXfile['Adj Close'])
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
        plt.plot(np.dot(my_S_[:,toremoveMin:toremoveMin+1], my_A_.T[toremoveMin:toremoveMin+1,:])[:,etfCounter], color ='Orange')
        my_S_=np.delete(my_S_,toremoveMin, axis=1)
        my_A_=np.delete(my_A_,toremoveMin, axis=1)
        plt.plot(np.dot(my_S_, my_A_.T)[:,etfCounter], color ='Blue')
        plt.plot(realSeries-(sum(realSeries)/len(realSeries)), color='Red')
        plt.show()
        counter+=1
    etfCounter+=1

    # plt.plot(np.dot(my_S_, my_A_.T)[:,etfCounter] + ica.mean_[etfCounter])
    # plt.plot(realSeries, color='Red')
    # plt.show()
    # etfCounter+=1

    # x_all = np.dot(my_S_, my_A_.T)[:,etfCounter] + ica.mean_[etfCounter]
    # x_all = MakeStationary(x_all['Adj Close'])
    # buys,sells,holds = GetSignals(XXfile)
    # x_buys = np.c_[x_all,]
    # X_train =x_all[(int)(x_all)*2/3),:]
    # X_train =x_all[(int)(x_all)*2/3),:]

    # clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    # clf.fit(X_train)
    # y_pred_train = clf.predict(X_train)
    # y_pred_test = clf.predict(X_test)
    # y_pred_outliers = clf.predict(X_outliers)
    # n_error_train = y_pred_train[y_pred_train == -1].size
    # n_error_test = y_pred_test[y_pred_test == -1].size
    # n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size

    # # plot the line, the points, and the nearest vectors to the plane
    # Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
    # Z = Z.reshape(xx.shape)

    # plt.title("Novelty Detection")
    # plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
    # a = plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
    # plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')

    # s = 40
    # b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c='white', s=s, edgecolors='k')
    # b2 = plt.scatter(X_test[:, 0], X_test[:, 1], c='blueviolet', s=s,
    #              edgecolors='k')
    # c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c='gold', s=s,
    #             edgecolors='k')
    # plt.axis('tight')
    # plt.xlim((-5, 5))
    # plt.ylim((-5, 5))
    # plt.legend([a.collections[0], b1, b2, c],
    #        ["learned frontier", "training observations",
    #         "new regular observations", "new abnormal observations"],
    #        loc="upper left",
    #        prop=matplotlib.font_manager.FontProperties(size=11))
    # plt.xlabel(
    #     "error train: %d/200 ; errors novel regular: %d/40 ; "
    #     "errors novel abnormal: %d/40"
    #     % (n_error_train, n_error_test, n_error_outliers))
    # plt.show()


    
    #for i in range(etfCounter, len(S_[etfCounter])):
    #   source = np.dot(S_[:,i:i+1], A_.T[i:i+1,:])[:,etfCounter]
    #   plt.plot(source)



