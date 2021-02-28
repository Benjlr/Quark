
import numpy as np
import pandas
from helpers import MakeIntoDF
from ib_insync.contract import Stock
from Trade import Trader
from IBpyFuncs import IBapi
from datetime import datetime, timedelta
from scipy import signal
from sklearn.decomposition import FastICA, PCA

etfs = [ 'EEM', 'EFA', 'EWA', 'EWC', 'EWJ', 'EWZ', 'FAS', 'FAZ', 'FXI',
'GDX', 'GLD', 'IGE', 'IWM', 'IYR', 'QID', 'QQQ', 'SDS', 'SKF','SPY', 'SSO', 'TZA', 'UNG',
'USO', 'VWO', 'VXX', 'XLE', 'XLF', 'XLI', 'XRT' ]

etfs2 = [ 'EWA', 'EWC']
#from the year of 2013–2015

app = Trader()
vxxcontract = Stock('XRT', exchange='SMART', currency='USD')
vxx = app.RetrieveHistoricalData(
    vxxcontract, 
    endDate= '20151231 23:59:59', #YYYYMMDD{SPACE}hh:mm:ss[{SPACE}TMZ]'.
    duration= '3 y', 
    barsize= '1 day')

vxx = MakeIntoDF(vxx)
#print(vxx)
#print(vxx['close'].pct_change().values)
s1 = pandas.Series(vxx['close'])
s1 = s1.pct_change().values[1:]
s1 = s1.reshape(-1,1)
#print(s1)

ica = FastICA(n_components = 10)
S_ = ica.fit_transform(s1)  # Reconstruct signals
A_ = ica.mixing_  # Get estimated mixing matrix

print(S_)
print(A_)
print(s1)
# We can `prove` that the ICA model applies by reverting the unmixing.
#assert np.allclose(X, np.dot(S_, A_.T) + ica.mean_)
