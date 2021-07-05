import pywt
import numpy as np
import pandas


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

def MakeStationary(series, log_stationary=False):
    if log_stationary:
        series=np.log10(series)

    s1 = pandas.Series(series).pct_change().values[1:].reshape(-1,1)
    s1 = s1-(sum(s1)/len(s1))
    s1 = (s1/max(s1,key=abs))
    return s1

def GetRHD(observed, source):
    myRHD =0
    for i in range(0, len(observed)-1):
        myRHD += (RHD(observed[i+1], observed[i]) - RHD(source[i+1], source[i]))**2
    return (1/(len(observed)-1))*myRHD
    

def RHD(tOne, t):
    if tOne - t > 0:
        return 1
    elif tOne - t < 0:
        return -1
    else :
        return 0

def GetSignals(data):
    rs = wave_smooth(data['Adj Close'],5)
    rs = np.insert(rs,0, np.zeros(len(data['Adj Close']) - len(rs)))
    sub_array=[j-i for i, j in zip(rs[:-1], rs[1:])] 
    sub_array= np.insert(sub_array, 0,0)
    zero_crossings = np.where(np.diff(np.signbit(sub_array)))[0]
    zero_crossings=np.delete(zero_crossings,0)
    signalsBuy =np.zeros(len(rs))
    SignalsSell =np.zeros(len(rs))
    SignalsHold =np.zeros(len(rs))

    for i in range(0,len(sub_array)):
        if i-1 in zero_crossings:
            if sub_array[i] > 0:
                SignalsSell[i]=-1
            else:
                signalsBuy[i]=1
        else:
            SignalsHold[i] =1
    return signalsBuy,SignalsSell,SignalsHold
    lastIndex =-1    
    returns =np.zeros(len(signals)-1)
    opens = np.array(data['Adj Close'])
    returns[0]=1000

    for i in range(1,len(signals)-1):
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

