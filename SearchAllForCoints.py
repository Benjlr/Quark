from detailed_coint import backtest, construct_lagged_portfolio, portfolio_halflife, portfolio_sharpe
from Cointegration import define_valid_series, find_coints, prepare_data_coint_test, print_trace_stat, test_stat
import os
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from Cointegration import find_coints, prepare_data_coint_test, print_trace_stat
import numpy as np
import pandas as pd

forex_directory = os.fsencode("C:\\Temp\\Data\\ETFS\\nasdaq")
etf_directory = os.fsencode("C:\\Temp\\Data\\ETFS\\nasdaq")

for files_forex in os.listdir(forex_directory):
    filename_forex = os.fsdecode(files_forex)
    if filename_forex.endswith(".csv"):
        forex_file = os.path.join(os.fsdecode(forex_directory),filename_forex)

        current_PathOne_series = prepare_data_coint_test(forex_file)
        if len(current_PathOne_series) < 252:
            continue

        for file_etf in os.listdir(etf_directory):
            etf_filename = os.fsdecode(file_etf)
            if etf_filename.endswith(".csv"): 
                try:
                    etf_file = os.path.join(os.fsdecode(etf_directory), etf_filename)
                    print(filename_forex + ':' + etf_filename)
                    samename = forex_file == etf_file
                    namelist =  (forex_file, etf_file)
                    namelist = sorted(namelist)
                    index = namelist.index(etf_file)
                    prevChecked = namelist
                    if(samename or index == 0):
                        print('skipped (name)')
                        continue
                
                    current_PathTwo_series = prepare_data_coint_test(etf_file)
                    if len(current_PathTwo_series) < 252:
                        print('skipped (length)')                    
                        continue
                
                    s1 = define_valid_series(current_PathOne_series,current_PathTwo_series)
                    resultJohans = coint_johansen(s1,0,1)
                    if test_stat(resultJohans):
                        yport = pd.DataFrame(np.dot(s1.values,resultJohans.evec[:, 0]))
                        lagged = construct_lagged_portfolio(yport)
                        hfl = portfolio_halflife(lagged)
                        if(hfl < 1):
                            continue
                        rets = backtest(s1,yport,hfl,resultJohans)
                        sharpe = portfolio_sharpe(rets)
                        f = open("C:\\Temp\\etf_results.txt", "a")   
                        f.write(filename_forex + ':' + etf_filename +','+str(hfl)+','+str(np.around(sharpe,2))+'\r')
                        print(str(hfl)+','+str(np.around(sharpe,2)))
                        f.close()
                except:
                    print('exception')
                    continue
            continue
    continue