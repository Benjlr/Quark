import pandas



def MakeIntoDF(file):
    df = pandas.DataFrame(file, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pandas.to_datetime(df['date']).dt.strftime("%d/%m/%Y %H:%M:%S")
    return df.set_index('date')

def SaveIBDataToFile(df, filename):
    df.to_csv(f'C:\\Temp\\{filename}.csv', header=None)  

def clean(file):
    cleanMe =True
    while cleanMe:
        m11 = file['open'] / file['open'].shift(-1) > 1.15 
        m12 = file['high'] / file['high'].shift(-1) > 1.15
        m13 = file['low'] / file['low'].shift(-1) > 1.15
        m14 = file['close'] / file['close'].shift(-1) > 1.15 
        m15 = file['open'].shift(-1) / file['open'] > 1.15 
        m16 = file['high'].shift(-1) / file['high'] > 1.15
        m17 = file['low'].shift(-1) / file['low'] > 1.15
        m18 = file['close'].shift(-1) / file['close'] > 1.15 
        startCount = len(file)
        file = file[~m11 & ~m12 & ~m13 & ~m14 & ~m15 & ~m16 & ~m17 & ~m18]
        cleanMe = startCount != len(file)


    return file



def PrimeKalman(kalman, df):
    for t in df.values:
        kalman.update_prediction(x_close= t[0], y_close= t[1])
        print(f'{kalman.iter}, BETA:{kalman.beta[:, kalman.iter]}')
