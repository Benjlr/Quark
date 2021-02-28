
from kalman import Kalman
from Cointegration import backtest, construct_lagged_portfolio, define_valid_series, portfolio_apr, portfolio_halflife, portfolio_sharpe, prepare_data_coint_test
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import statsmodels.tsa.stattools as ts
import statsmodels.tsa.vector_ar.vecm as vm


factor = 1

#XXfile = "testdata\\EWA.csv"
#YYfile = "testdata\\EWC.csv"
XXfile = "C:\\Temp\\Data\\ETFS\\Arca\\AAAU.csv"
YYfile = "C:\\Temp\\Data\\ETFS\\Arca\\AFIF.csv"

df_x = prepare_data_coint_test(XXfile)
df_y = prepare_data_coint_test(YYfile)
s1 = define_valid_series(df_x, df_y)
print('series length ' + str(len(s1)))


coint_result =vm.coint_johansen(s1, 0,1)
yport = pd.DataFrame(np.dot(s1.values,coint_result.evec[:, 0]))
yport_lagged = construct_lagged_portfolio(yport) 
halflife = portfolio_halflife(yport_lagged)
returns = backtest(s1,yport,halflife,coint_result)
pd.DataFrame((np.cumprod(1+returns)-1)).plot()
print(halflife)
print('APR=%f Sharpe=%f' % (portfolio_apr(returns), portfolio_sharpe(returns)))

### KALMAN
x=s1['close_x']
y=s1['close_y']

x=np.array(ts.add_constant(x))[:, [1,0]] # Augment x with ones to  accomodate possible offset in the regression between y vs x.
delta=0.0001 # delta=1 gives fastest change in beta, delta=0.000....1 allows no change (like traditional linear regression).

yhat=np.full(y.shape[0], np.nan) # measurement prediction
e=yhat.copy()
Q=yhat.copy()

# For clarity, we denote R(t|t) by P(t). Initialize R, P and beta.
R=np.zeros((2,2))
P=R.copy()
beta=np.full((2, x.shape[0]), np.nan)
Vw=delta/(1-delta)*np.eye(2)
Ve=0.001

# Initialize beta(:, 1) to zero
beta[:, 0]=0
# Given initial beta and R (and P)
for t in range(len(y)):
    if t > 0:
        beta[:, t]=beta[:, t-1]
        R=P+Vw
            
    yhat[t]=np.dot(x[t, :], beta[:, t])
    #print('FIRST: yhat[t]=', yhat[t])
    
    Q[t]=(np.dot(np.dot(x[t, :], R), x[t, :].T)+Ve)
    #print('Q[t]=', Q[t])

    # Observe y(t)
    e[t]=y[t]-yhat[t] # measurement prediction error
#    print('e[t]=', e[t])
#    print('SECOND: yhat[t]=', yhat[t])
    
    K=np.dot(R, x[t, :].T)/Q[t] #  Kalman gain
#    print(K)
    
    beta[:, t]=beta[:, t]+np.dot(K, e[t]) #  State update. Equation 3.11
#    print(beta[:, t])
    
    # P=R-np.dot(np.dot(K, x[t, :]), R) # State covariance update. Euqation 3.12
    P=R-np.dot(np.outer(K, x[t, :]), R) # Thanks to Matthias for chaning np.dot -> np.outer!

#    print(R)


#plt.plot(beta[0, :])
#plt.plot(beta[1, :])
plt.plot(e[30:])
plt.plot(np.sqrt(Q[30:])* factor)
plt.plot(-np.sqrt(Q[30:])* factor)
#print(e)


longsEntry=e < -np.sqrt(Q)* factor
longsExit =e > 0

shortsEntry=e > np.sqrt(Q)* factor
shortsExit =e < 0

numUnitsLong=np.zeros(longsEntry.shape)
numUnitsLong[:]=np.nan

numUnitsShort=np.zeros(shortsEntry.shape)
numUnitsShort[:]=np.nan

numUnitsLong[0]=0
numUnitsLong[longsEntry]=1
numUnitsLong[longsExit]=0
numUnitsLong=pd.DataFrame(numUnitsLong)
numUnitsLong.fillna(method='ffill', inplace=True)

numUnitsShort[0]=0
numUnitsShort[shortsEntry]=-1
numUnitsShort[shortsExit]=0
numUnitsShort=pd.DataFrame(numUnitsShort)
numUnitsShort.fillna(method='ffill', inplace=True)

numUnits=numUnitsLong+numUnitsShort
positions=pd.DataFrame(np.tile(numUnits.values, [1, 2]) * ts.add_constant(-beta[0,:].T)[:, [1,0]] *s1.values) 
#  [hedgeRatio -ones(size(hedgeRatio))] is the shares allocation, [hedgeRatio -ones(size(hedgeRatio))].
# *y2 is the dollar capital allocation, while positions is the dollar capital in each ETF.
pnl=np.sum((positions.shift().values)*(s1.pct_change().values), axis=1) # daily P&L of the strategy
ret=pnl/np.sum(np.abs(positions.shift()), axis=1)
ret =np.nan_to_num(ret)

x= np.c_[ x, y, yhat, e, Q, longsEntry, longsExit, shortsEntry, shortsExit, numUnitsLong, numUnitsShort, numUnits, positions, pnl,ret ]

np.savetxt( 'c:\\Temp\\dadat.csv', x, delimiter=',')
np.savetxt( 'c:\\Temp\\beta.csv', beta, delimiter=',')

pd.DataFrame((np.cumprod(1+ret)-1)).plot()

print('kalman')
print('APR=%f Sharpe=%f' % (portfolio_apr(ret), portfolio_sharpe(ret)))
#APR=0.313225 Sharpe=3.464060
 

myKal = Kalman()
print(len(s1.values))
for t in s1.values:

    myKal.update_prediction(x_close= t[0], y_close= t[1])

longsEntry=myKal.e < -np.sqrt(myKal.Q)* factor
longsExit =myKal.e > -np.sqrt(myKal.Q)* factor

shortsEntry=myKal.e > np.sqrt(myKal.Q)* factor
shortsExit =myKal.e < np.sqrt(myKal.Q)* factor

numUnitsLong=np.zeros(longsEntry.shape)
numUnitsLong[:]=np.nan

numUnitsShort=np.zeros(shortsEntry.shape)
numUnitsShort[:]=np.nan

numUnitsLong[0]=0
numUnitsLong[longsEntry]=1
numUnitsLong[longsExit]=0
numUnitsLong=pd.DataFrame(numUnitsLong)
numUnitsLong.fillna(method='ffill', inplace=True)

numUnitsShort[0]=0
numUnitsShort[shortsEntry]=-1
numUnitsShort[shortsExit]=0
numUnitsShort=pd.DataFrame(numUnitsShort)
numUnitsShort.fillna(method='ffill', inplace=True)

numUnits=numUnitsLong+numUnitsShort
positions=pd.DataFrame(np.tile(numUnits.values, [1, 2]) * ts.add_constant(-myKal.beta[0,1:].T)[:, [1,0]] *s1.values) 
#  [hedgeRatio -ones(size(hedgeRatio))] is the shares allocation, [hedgeRatio -ones(size(hedgeRatio))].
# *y2 is the dollar capital allocation, while positions is the dollar capital in each ETF.
pnl=np.sum((positions.shift().values)*(s1.pct_change().values), axis=1) # daily P&L of the strategy
ret=pnl/np.sum(np.abs(positions.shift()), axis=1)
ret =np.nan_to_num(ret)

pd.DataFrame((np.cumprod(1+ret)-1)).plot()

print('Tester')
print('APR=%f Sharpe=%f' %  (portfolio_apr(ret), portfolio_sharpe(ret)))


plt.show()

