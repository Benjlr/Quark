from Cointegration import backtest, construct_lagged_portfolio, define_valid_series, find_coints, portfolio_apr, portfolio_halflife, portfolio_sharpe, prepare_data_coint_test, print_trace_stat, test_stat
import os
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from Cointegration import find_coints, prepare_data_coint_test, print_trace_stat
import numpy as np
import pandas as pd

arcoOneRoot = "C:\\Temp\\Data\\ETFS\\Arca"
arcaTwoRoot = "C:\\Temp\\Data\\ETFS\\Arca"

arcaOne = sorted(os.listdir(os.fsencode(arcoOneRoot)))
arcaTwo = sorted(os.listdir(os.fsencode(arcaTwoRoot)))

for file_Arca_One in arcaOne:

    file_Arca_One = os.fsdecode(file_Arca_One)
    file_Arca_One = os.path.join(os.fsdecode(arcoOneRoot),file_Arca_One)

    current_Arca_One_Datum = prepare_data_coint_test(file_Arca_One)
    if len(current_Arca_One_Datum) < 252:
        print('skipped (length)')  
        continue

    if (current_Arca_One_Datum.loc['2021-01-31':'2021-01-23']['volume'].sum() * current_Arca_One_Datum.head(1)['close']).values[0] < 1000000:
        print("skipped - volume")
        continue

    for file_Arca_Two in arcaTwo:
        try:
    
            file_Arca_Two = os.fsdecode(file_Arca_Two) 

            file_Arca_Two = os.path.join(os.fsdecode(arcaTwoRoot), file_Arca_Two)
            print(file_Arca_One + ':' + file_Arca_Two)
            samename = file_Arca_One == file_Arca_Two
            namelist =  (file_Arca_One, file_Arca_Two)
            namelist = sorted(namelist)
            index = namelist.index(file_Arca_Two)
            prevChecked = namelist
            if(samename or index == 0):
                print('skipped (name)')
                continue
                
            current_Arca_Two_Datum = prepare_data_coint_test(file_Arca_Two)
            if len(current_Arca_Two_Datum) < 252:
                print('skipped (length)')                    
                continue

            if (current_Arca_Two_Datum.loc['2021-01-31':'2021-01-23']['volume'].sum() * current_Arca_Two_Datum.head(1)['close']).values[0] < 1000000:
                print("skipped - volume")
                continue
                
            s1 = define_valid_series(current_Arca_One_Datum,current_Arca_Two_Datum)
            resultJohans = coint_johansen(s1,0,1)

            if test_stat(resultJohans):
                yport = pd.DataFrame(np.dot(s1.values,resultJohans.evec[:, 0]))
                lagged = construct_lagged_portfolio(yport)
                hfl = portfolio_halflife(lagged)

                rets = backtest(s1,yport,hfl,resultJohans)
                sharpe = portfolio_sharpe(rets)
                apr = portfolio_apr(rets)
                f = open("C:\\Temp\\etf_results.txt", "a")   
                f.write(file_Arca_One + ':' + file_Arca_Two +','+str(hfl)+', SHARPE: '+str(np.around(sharpe,2))+', APR: '+str(np.around(apr,2))+'\r')
                print(str(hfl)+','+str(np.around(sharpe,2)))
                f.close()
            else:
                print("failed test")
        except:
            print("oops")
        continue
    continue