from numpy.core.fromnumeric import take
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import statsmodels.tsa.stattools as ts
import statsmodels.tsa.vector_ar.vecm as vm
import numpy as np
import pandas as pd
import statsmodels.formula.api as sm

mindate = '2018-06-01'
maxdate = '2023-04-09'

def prepare_data_coint_test(path):
    df_x = pd.read_csv(path, sep=r'\s*,\s*', engine='python', header=None, index_col=['date'], names=["date", "open", "high", "low", "close","volume"], parse_dates=['date'], dayfirst=True)
    #df_x = df_x.loc[:mindate]
    #df_x = resample(df_x)
    return df_x

def resample(data):
    return data.resample('d').agg({'open': 'first', 
                               'high': 'max',
                               'low': 'min',
                               'close': 'last'},
                              # 'Volume': 'sum'}, 
                               loffset = pd.offsets.Day(1))


def print_trace_stat(res):  
    if res == None:
        return 'series too short'

    result ="trace stat"
    result +="\nr <= 0 "
    if res.trace_stat[0] > res.trace_stat_crit_vals[0][2]:
        result += ('rejected (>99%)')
    elif res.trace_stat[0] > res.trace_stat_crit_vals[0][1]:
        result += ('rejected (>95%)')
    elif res.trace_stat[0] > res.trace_stat_crit_vals[0][0]:
        result += ('rejected (>90%)')
    else:
        result += ('not rejected')
    
    result += '\nr <= 1 '
    if res.trace_stat[1] > res.trace_stat_crit_vals[1][2]:
        result += ('rejected (>99%)')
    elif res.trace_stat[1] > res.trace_stat_crit_vals[1][1]:
        result += ('rejected (>95%)')
    elif res.trace_stat[1] > res.trace_stat_crit_vals[1][0]:
        result += ('rejected (>90%)')
    else:
        result += ('not rejected')

    result +="\neigen stat"
    result +="\nr <= 0 "
    if res.max_eig_stat[0] > res.max_eig_stat_crit_vals[0][2]:
        result += ('rejected (>99%)')
    elif res.max_eig_stat[0] > res.max_eig_stat_crit_vals[0][1]:
        result += ('rejected (>95%)')
    elif res.max_eig_stat[0] > res.max_eig_stat_crit_vals[0][0]:
        result += ('rejected (>90%)')
    else:
        result += ('not rejected')
    
    result += '\nr <= 1 '
    if res.max_eig_stat[1] > res.max_eig_stat_crit_vals[1][2]:
        result += ('rejected (>99%)')
    elif res.max_eig_stat[1] > res.max_eig_stat_crit_vals[1][1]:
        result += ('rejected (>95%)')
    elif res.max_eig_stat[1] > res.max_eig_stat_crit_vals[1][0]:
        result += ('rejected (>90%)')
    else:
        result += ('not rejected')

    return result

def test_stat(res):  
    if res.trace_stat[0] > res.trace_stat_crit_vals[0][0]:
        return True
    if res.trace_stat[1] > res.trace_stat_crit_vals[1][0]:
        return True

    if res.max_eig_stat[0] > res.max_eig_stat_crit_vals[0][0]:
        return True
    if res.max_eig_stat[1] > res.max_eig_stat_crit_vals[1][0]:
        return True

    return False


def define_valid_series(df_x, df_y):
    s1 = pd.merge(df_x['close'], df_y['close'], how='inner', on=['date'])
    #df = df[df['x'].notna()]
    #df = df[df['y'].notna()]
    s1 = s1.sort_values(by='date')
    return s1

def find_coints(pathOne,pathTwo):
    df_x = prepare_data_coint_test(pathOne)
    df_y = prepare_data_coint_test(pathTwo)
    return coint_johansen(define_valid_series(df_x,df_y),0,1)

def construct_lagged_portfolio(yport):
    yport_lag = yport.shift()
    delta_yport = yport - yport_lag 
    df2=pd.concat([yport_lag, delta_yport], axis=1)
    df2.columns=['ylag', 'deltaY']
    return df2

def portfolio_halflife(lagged_portfolio):
    regress_results=sm.ols(formula="deltaY ~ ylag", data=lagged_portfolio).fit()
    return np.round(-np.log(2)/regress_results.params['ylag']).astype(int)

def backtest(s1, yport, halflife, johansen_vect):
    numUnits = -(yport - yport.rolling(halflife).mean())/yport.rolling(halflife).std()
    positions=pd.DataFrame(np.dot(numUnits.values, np.expand_dims(johansen_vect.evec[:, 0], axis=1).T)*s1.values) 

    pnl=np.sum((positions.shift().values)*(s1.pct_change().values), axis=1) 
    ret=pnl/np.sum(np.abs(positions.shift()), axis=1)
    return ret

def portfolio_sharpe(ret, periods = 252):
    return np.sqrt(periods)*np.mean(ret)/np.std(ret)

def portfolio_apr(ret, periods =252):
    return np.prod(1+ret)**(periods/len(ret))-1


def kalman_backtest(s1):
    ### KALMAN
    x=s1['close_x']
    y=s1['close_y']

    x=np.array(ts.add_constant(x))[:, [1,0]]
    delta=0.0001
    yhat=np.full(y.shape[0], np.nan)
    e=yhat.copy()
    Q=yhat.copy()

    R=np.zeros((2,2))
    P=R.copy()
    beta=np.full((2, x.shape[0]), np.nan)
    Vw=delta/(1-delta)*np.eye(2)
    Ve=0.001
    beta[:, 0]=0
    for t in range(len(y)):
        if t > 0:
            beta[:, t]=beta[:, t-1]
            R=P+Vw
            
        yhat[t]=np.dot(x[t, :], beta[:, t])
    
        Q[t]=(np.dot(np.dot(x[t, :], R), x[t, :].T)+Ve)
        e[t]=y[t]-yhat[t] 
        K=np.dot(R, x[t, :].T)/Q[t] 
        beta[:, t]=beta[:, t]+np.dot(K, e[t]) 
        P=R-np.dot(np.outer(K, x[t, :]), R)

        longsEntry=e < -np.sqrt(Q)
        longsExit =e > 0

        shortsEntry=e > np.sqrt(Q)
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
        pnl=np.sum((positions.shift().values)*(s1.pct_change().values), axis=1)
        ret=pnl/np.sum(np.abs(positions.shift()), axis=1)
        return np.nan_to_num(ret)



