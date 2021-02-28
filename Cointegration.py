from numpy.core.fromnumeric import take
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen

mindate = '2018-06-01'
maxdate = '2023-04-09'

def prepare_data_coint_test(path):
    df_x = pd.read_csv(path, sep=r'\s*,\s*', engine='python', header=None, index_col=['date'], names=["date", "open", "high", "low", "close"], parse_dates=['date'], dayfirst=True)
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





