import numpy as np
from numpy.core.defchararray import array
from numpy.core.fromnumeric import shape
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core import series
import statsmodels.formula.api as sm
import statsmodels.tsa.stattools as ts
import statsmodels.tsa.vector_ar.vecm as vm



class Kalman:
    x = np.ndarray(shape=[0,2])
    y = []
    yhat = np.array([],float)
    Q = np.array([],float)
    e = np.array([],float)


    def __init__(self):        
        self.R = np.zeros((2,2))
        self.delta=0.000001
        self.beta=np.ndarray(shape=[2,0])
        self.Vw=self.delta/(1-self.delta)*np.eye(2)
        self.Ve=0.001


    def update_prediction(self, x_close, y_close):   
        self.x = np.append(self.x, [[x_close,1]], axis=0) 
        self.y = np.append(self.y, y_close)
        iter = len(self.y)-1
        
        if(iter< 1):
            self.beta = np.append(self.beta, [[0], [0]] , axis=1) 

        if(iter > 0):
            #self.beta = np.append(self.beta, [[self.beta[0,iter-1]], [self.beta[1,iter-1]]] , axis=1) 
            self.R=self.P+self.Vw

        self.yhat = np.append(self.yhat, np.dot(self.x[iter, :], self.beta[:, iter]))
        self.Q= np.append(self.Q, np.dot(np.dot(self.x[iter, :], self.R), self.x[iter, :].T)+self.Ve)
        self.e= np.append(self.e, self.y[iter]-self.yhat[iter]) 
        K=np.dot(self.R, self.x[iter, :].T)/self.Q[iter] 
        self.beta = np.append(self.beta, [[(self.beta[0, iter]+np.dot(K, self.e[iter])[0])], 
        [(self.beta[1, iter]+np.dot(K, self.e[iter])[1])]] , axis=1) 
        self.P=self.R-np.dot(np.outer(K, self.x[iter, :]), self.R) # Thanks to Matthias for chaning np.dot -> np.outer!

