import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import pywt
import matplotlib.pyplot as plt
import yfinance as yf  
import wavelet_funcs

XXfile = yf.download('EWA','2013-01-01','2016-01-01')
rs = wavelet_funcs.wave_smooth(XXfile['Adj Close'],5)
atation = wavelet_funcs.MakeStationary(XXfile['Adj Close'])

#rs = np.insert(rs,0, np.zeros(len(XXfile['Adj Close']) - len(rs)))
# Number of samplepoints
N = 700
# sample spacing
T = 1.0 / 200
x = np.linspace(0.0, N*T, N)
y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
yf = scipy.fftpack.fft(atation)
xf = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.plot(atation)
plt.show()