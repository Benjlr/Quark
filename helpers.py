import pandas



def MakeIntoDF(file):
    df = pandas.DataFrame(file, columns=['date', 'open', 'high', 'low', 'close'])
    df['date'] = pandas.to_datetime(df['date']).dt.strftime("%d/%m/%Y %H:%M:%S")
    return df.set_index('date')

def SaveIBDataToFile(df, filename):
    df.to_csv(f'C:\\Temp\\{filename}.csv', header=None)  

def PrimeKalman(kalman, df):
    for t in df.values:
        kalman.update_prediction(x_close= t[0], y_close= t[1])
        print(f'{kalman.iter}, BETA:{kalman.beta[:, kalman.iter]}')
