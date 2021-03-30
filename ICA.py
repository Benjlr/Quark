
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



etfs = [ 'EEM', 'EFA', 'EWA', 'EWC', 'EWJ', 'EWZ', 'FAS', 'FAZ', 'FXI',
'GDX', 'GLD', 'IGE', 'IWM', 'IYR', 'QID', 'QQQ', 'SDS', 'SKF','SPY', 'SSO', 'TZA', 'UNG',
'USO', 'VWO', 'VXX', 'XLE', 'XLF', 'XLI', 'XRT' ]

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

XXfile = prepare_data_coint_test("C:\\Temp\\EWC.csv")
#c1,c2 = XXfile[:352],XXfile[352:]
#print(c1)
#print(c2)

rs = wave_smooth(XXfile['close'],5)
rs = np.insert(rs,0, np.zeros(len(XXfile['close']) - len(rs)))
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
returns =np.zeros(len(signals))
opens = np.array(XXfile['open'])
returns[0]=1000

for i in range(1,len(signals)):
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

print(returns[len(returns)-1])



np.savetxt("C:\Temp\waves.csv", rs, delimiter=",")
np.savetxt("C:\Temp\diffs.csv", sub_array, delimiter=",")
np.savetxt("C:\Temp\zeroes.csv", zero_crossings, delimiter=",")
np.savetxt("C:\Temp\\signals.csv", signals, delimiter=",")
np.savetxt("C:\Temp\\returns.csv", returns, delimiter=",")

#spectrum = create_spectrum(rs)
#spectrum = spectrum**2
#plt.imshow(spectrum,cmap='Spectral')
#plt.show()

'''
s1 = pandas.Series(vxx['close'])
s1 = s1.pct_change().values[1:]
s1 = s1.reshape(-1,1)
print(s1)

ica = FastICA(n_components = 10)
S_ = ica.fit_transform(s1)  # Reconstruct signals
A_ = ica.mixing_  # Get estimated mixing matrix

print(S_)
print(A_)
print(s1)
# We can `prove` that the ICA model applies by reverting the unmixing.
assert np.allclose(X, np.dot(S_, A_.T) + ica.mean_)
'''


