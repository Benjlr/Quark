from numpy.core.fromnumeric import take
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen
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

def portfolio_sharpe(ret):
    return np.sqrt(252*24)*np.mean(ret)/np.std(ret)

def portfolio_apr(ret):
    return np.prod(1+ret)**(252*24/len(ret))-1




